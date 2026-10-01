import { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { BookOpen, GraduationCap, Layers, Sparkles, TriangleAlert, UserRound, UsersRound } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Avatar } from '../../components/ui/Avatar';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { ListSkeleton, Skeleton } from '../../components/ui/Skeleton';
import { proxyService } from '../../services/proxyService';
import { parseApiError } from '../../lib/errors';
import { formatLongDate } from '../../lib/dates';
import { cn } from '../../lib/utils';
import { ProxyCandidate } from '../../types';

export function CandidatePage() {
  const { requirementId } = useParams<{ requirementId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const requirement = useQuery({
    queryKey: ['proxy-requirement', requirementId],
    queryFn: () => proxyService.getRequirement(requirementId!),
    enabled: !!requirementId,
  });

  const candidates = useQuery({
    queryKey: ['candidates', requirementId],
    queryFn: () => proxyService.getCandidates(requirementId!),
    enabled: !!requirementId,
  });

  // The server already ranks; the recommended teacher always leads.
  const sorted = useMemo(() => {
    const list = candidates.data ?? [];
    return [...list].sort((a, b) => Number(b.is_recommended) - Number(a.is_recommended) || a.rank - b.rank);
  }, [candidates.data]);

  const assign = useMutation({
    mutationFn: (c: ProxyCandidate) => proxyService.assignProxy(requirementId!, c.teacher_id),
    onSuccess: (_d, c) => {
      toast.success(`${c.teacher_name} assigned`, { description: requirement.data ? `Covering period ${requirement.data.period_number} for ${requirement.data.class_name}.` : undefined });
      navigate(-1);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['proxy-requirements'] });
      queryClient.invalidateQueries({ queryKey: ['proxy-requirement', requirementId] });
      queryClient.invalidateQueries({ queryKey: ['proxy-assignments'] });
      // The assigned teacher is now busy for every other pending period in this slot.
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
    },
  });

  const assignError = assign.isError ? parseApiError(assign.error) : null;
  const req = requirement.data;
  const alreadyCovered = req?.status === 'ASSIGNED';

  return (
    <Page>
      <PageHeader eyebrow="Assign a proxy" title="Available teachers" description={req ? formatLongDate(req.date) : undefined} />

      {requirement.isLoading ? (
        <Skeleton className="h-24 w-full rounded-xl" />
      ) : req ? (
        <Card variant="accent" className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="inline-flex h-7 min-w-[2rem] items-center justify-center rounded-md bg-primary px-1.5 text-xs font-bold tabular-nums text-white">P{req.period_number}</span>
            <p className="font-bold">{req.class_name}{req.subject ? ` · ${req.subject}` : ''}</p>
          </div>
          <p className="flex items-center gap-1.5 text-sm text-text-secondary">
            <UserRound size={14} aria-hidden /> {req.absent_teacher_name} is absent
          </p>
          {alreadyCovered && (
            <p className="text-sm font-semibold text-success">Already covered by {req.assigned_proxy_teacher_name}.</p>
          )}
        </Card>
      ) : null}

      <section aria-label="Candidates" className="space-y-3">
        {candidates.isLoading ? (
          <ListSkeleton rows={3} />
        ) : candidates.error ? (
          <ErrorState title="Couldn't load candidates" onRetry={() => candidates.refetch()} />
        ) : sorted.length === 0 ? (
          <EmptyState
            icon={<UsersRound size={26} />}
            title="No one is free"
            description="Everyone is absent, teaching another class, or already covering a proxy this period."
            action={<Button variant="secondary" onClick={() => navigate(-1)}>Go back</Button>}
          />
        ) : (
          <>
            <p className="text-sm text-text-secondary">
              {sorted.length} teacher{sorted.length === 1 ? '' : 's'} free. Ranked by class match first, then subject, then fewest proxies today.
            </p>
            <ul className="space-y-3">
              {sorted.map((c, i) => (
                <li key={c.teacher_id}>
                  <CandidateCard candidate={c} position={i + 1} disabled={assign.isPending || alreadyCovered} busy={assign.isPending && assign.variables?.teacher_id === c.teacher_id} onAssign={() => assign.mutate(c)} />
                </li>
              ))}
            </ul>
          </>
        )}

        {assignError && (
          <div role="alert" className="flex items-start gap-2 rounded-xl border border-error/30 bg-error-bg p-3">
            <TriangleAlert size={16} className="mt-0.5 shrink-0 text-error" aria-hidden />
            <div>
              <p className="text-sm font-semibold text-error">{assignError.status === 409 ? 'Availability changed' : "Couldn't assign"}</p>
              <p className="mt-0.5 text-xs text-error/90">{assignError.message}{assignError.status === 409 ? ' The list has been refreshed.' : ''}</p>
            </div>
          </div>
        )}
      </section>
    </Page>
  );
}

function CandidateCard({ candidate: c, position, disabled, busy, onAssign }: { candidate: ProxyCandidate; position: number; disabled: boolean; busy: boolean; onAssign: () => void }) {
  return (
    <Card variant={c.is_recommended ? 'accent' : 'raised'} className={cn('space-y-3', c.is_recommended && 'ring-1 ring-accent/40')}>
      <div className="flex items-center gap-3">
        <Avatar name={c.teacher_name} />
        <div className="min-w-0 flex-1">
          <p className="truncate font-bold">{c.teacher_name}</p>
          <p className="text-xs text-text-secondary">
            {c.proxy_count_today === 0 ? 'No proxies yet today' : `${c.proxy_count_today} prox${c.proxy_count_today === 1 ? 'y' : 'ies'} already today`}
          </p>
        </div>
        {c.is_recommended ? (
          <Badge tone="gold"><Sparkles size={12} aria-hidden /> Best fit</Badge>
        ) : (
          <span className="text-xs font-bold tabular-nums text-text-muted" aria-label={`Rank ${position}`}>#{position}</span>
        )}
      </div>

      {(c.class_match || c.subject_match) && (
        <div className="flex flex-wrap gap-1.5">
          {c.class_match === 'exact' && <Badge tone="navy"><GraduationCap size={12} aria-hidden /> Teaches this class</Badge>}
          {c.class_match === 'same_standard' && <Badge tone="navy"><Layers size={12} aria-hidden /> Same standard, other division</Badge>}
          {c.subject_match && <Badge tone="success"><BookOpen size={12} aria-hidden /> Same subject</Badge>}
        </div>
      )}

      <Button className="w-full" variant={c.is_recommended ? 'primary' : 'secondary'} onClick={onAssign} disabled={disabled} isLoading={busy}>
        Assign {c.teacher_name.split(' ').filter((p) => !/^(mr|mrs|ms|miss|dr)\.?$/i.test(p))[0] ?? 'proxy'}
      </Button>
    </Card>
  );
}
