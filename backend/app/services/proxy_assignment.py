from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.proxy import ProxyAssignment, ProxyRequirement, RequirementStatus
from app.models.audit import AuditEvent
from app.core.exceptions import ConflictException
from datetime import datetime, timezone
import uuid

async def assign_proxy(db: AsyncSession, requirement_id: uuid.UUID, proxy_teacher_id: uuid.UUID, supervisor_id: uuid.UUID):
    # SELECT FOR UPDATE to prevent concurrent assignment to the same requirement
    stmt = select(ProxyRequirement).where(ProxyRequirement.id == requirement_id).with_for_update()
    req = (await db.execute(stmt)).scalar_one_or_none()
    
    if not req:
        raise ConflictException("Requirement not found")
        
    if req.status == RequirementStatus.ASSIGNED:
        db.add(AuditEvent(
            actor_id=supervisor_id,
            event_type="ASSIGNMENT_COLLISION_PREVENTED",
            entity_type="ProxyRequirement",
            entity_id=requirement_id,
            metadata_json={"proxy_teacher_id": str(proxy_teacher_id), "reason": "requirement_already_assigned"}
        ))
        await db.commit()
        raise ConflictException("Requirement is already assigned")

    # Re-validate constraint 3: not already assigned for this slot
    pa_check = select(ProxyAssignment).join(
        ProxyRequirement, ProxyAssignment.requirement_id == ProxyRequirement.id
    ).where(
        ProxyRequirement.date == req.date,
        ProxyRequirement.period_number == req.period_number,
        ProxyAssignment.proxy_teacher_id == proxy_teacher_id,
        ProxyAssignment.cancelled_at.is_(None)
    )
    existing_assignment = (await db.execute(pa_check)).scalar_one_or_none()
    if existing_assignment:
        db.add(AuditEvent(
            actor_id=supervisor_id,
            event_type="ASSIGNMENT_COLLISION_PREVENTED",
            entity_type="ProxyRequirement",
            entity_id=requirement_id,
            metadata_json={"proxy_teacher_id": str(proxy_teacher_id), "reason": "already_assigned_this_period"}
        ))
        await db.commit()
        raise ConflictException("Teacher already assigned to another proxy in this period")

    assignment = ProxyAssignment(
        requirement_id=requirement_id,
        proxy_teacher_id=proxy_teacher_id,
        date=req.date,
        period_number=req.period_number,
        assigned_by=supervisor_id
    )
    db.add(assignment)

    try:
        # Flush so assignment.id is populated before the audit row captures it
        # (the UUID default only fires at INSERT, not object construction),
        # and so the partial unique index is checked before we commit.
        await db.flush()

        req.status = RequirementStatus.ASSIGNED

        audit = AuditEvent(
            actor_id=supervisor_id,
            event_type="ASSIGNMENT_CREATED",
            entity_type="ProxyAssignment",
            entity_id=assignment.id,
            metadata_json={"requirement_id": str(requirement_id), "proxy_teacher_id": str(proxy_teacher_id)}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(assignment)
        return assignment
    except IntegrityError:
        # Final safety net: the partial unique index on (date, period_number,
        # proxy_teacher_id) rejects a genuine cross-requirement race that the
        # pre-check above cannot fully prevent by itself.
        await db.rollback()
        db.add(AuditEvent(
            actor_id=supervisor_id,
            event_type="ASSIGNMENT_COLLISION_PREVENTED",
            entity_type="ProxyRequirement",
            entity_id=requirement_id,
            metadata_json={"proxy_teacher_id": str(proxy_teacher_id), "reason": "concurrent_race"}
        ))
        await db.commit()
        raise ConflictException("This teacher was assigned elsewhere. We refreshed the available teachers.")
    except Exception as e:
        await db.rollback()
        raise ConflictException(f"Failed to assign proxy: {str(e)}")

async def cancel_assignment(db: AsyncSession, assignment_id: uuid.UUID, supervisor_id: uuid.UUID):
    stmt = select(ProxyAssignment).where(ProxyAssignment.id == assignment_id)
    assignment = (await db.execute(stmt)).scalar_one_or_none()
    
    if not assignment or assignment.cancelled_at:
        return
        
    assignment.cancelled_at = datetime.now(timezone.utc)
    
    req_stmt = select(ProxyRequirement).where(ProxyRequirement.id == assignment.requirement_id)
    req = (await db.execute(req_stmt)).scalar_one_or_none()
    if req:
        req.status = RequirementStatus.PENDING
        
    audit = AuditEvent(
        actor_id=supervisor_id,
        event_type="ASSIGNMENT_CANCELLED",
        entity_type="ProxyAssignment",
        entity_id=assignment.id,
        metadata_json={"requirement_id": str(assignment.requirement_id)}
    )
    db.add(audit)
    
    await db.commit()
