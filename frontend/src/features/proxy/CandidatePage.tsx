import { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { Heart, Sparkles, TriangleAlert } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Avatar } from '../../components/ui/Avatar';
import { Skeleton } from '../../components/ui/Skeleton';
import { proxyService } from '../../services/proxyService';
import { favoritesService } from '../../services/favoritesService';

export function CandidatePage() {
  const { requirementId } = useParams<{ requirementId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: candidates = [], isLoading, error } = useQuery({
    queryKey: ['candidates', requirementId],
    queryFn: () => proxyService.getCandidates(requirementId!),
    enabled: !!requirementId,
  });

  const { data: favorites = [] } = useQuery({
    queryKey: ['favorites'],
    queryFn: () => favoritesService.getFavorites(),
  });
  const favoriteIds = useMemo(() => new Set(favorites.map((f) => f.teacher_id)), [favorites]);

  const favoriteMutation = useMutation({
    mutationFn: ({ teacherId, isFavorite }: { teacherId: string; isFavorite: boolean }) =>
      isFavorite ? favoritesService.removeFavorite(teacherId) : favoritesService.addFavorite(teacherId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['favorites'] }),
  });

  // The recommended candidate always leads (design.md: "Recommended candidate
  // first") - favorites only reorder the remaining eligible candidates, and
  // never affect which candidates are eligible in the first place.
  const sortedCandidates = useMemo(() => {
    const recommended = candidates.filter((c: any) => c.is_recommended);
    const others = candidates.filter((c: any) => !c.is_recommended);
    others.sort((a: any, b: any) => {
      const aFav = favoriteIds.has(a.teacher_id) ? 0 : 1;
      const bFav = favoriteIds.has(b.teacher_id) ? 0 : 1;
      return aFav - bFav;
    });
    return [...recommended, ...others];
  }, [candidates, favoriteIds]);

  const assignMutation = useMutation({
    mutationFn: (proxyTeacherId: string) =>
      proxyService.assignProxy(requirementId!, proxyTeacherId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proxy-requirements'] });
      // The assigned teacher is now unavailable for any other pending period
      // in this same slot - refresh other open candidate lists too.
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      navigate(-1);
    },
    onError: () => {
      // design.md: "Never hide a collision error behind a generic toast" and
      // "refresh the slot and explain that availability changed" - so a 409
      // (someone else took this candidate) must re-pull the candidate list,
      // not just show an error and leave stale entries on screen.
      queryClient.invalidateQueries({ queryKey: ['candidates', requirementId] });
    },
  });

  const assignErrorMessage = isAxiosError(assignMutation.error)
    ? (assignMutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined;
  const isCollision = assignMutation.isError && assignMutation.error && isAxiosError(assignMutation.error) && assignMutation.error.response?.status === 409;

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        <Skeleton className="h-7 w-48" />
        <Skeleton className="h-4 w-64" />
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-surface-elevated p-4 rounded-xl border border-border space-y-3">
              <div className="flex items-center gap-3">
                <Skeleton className="w-10 h-10 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-40" />
                </div>
              </div>
              <Skeleton className="h-11 w-full rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-error">Failed to load candidates. Please try again.</div>
    );
  }

  return (
    <div className="p-4 space-y-4 animate-fade-in">
      <div>
        <h1 className="text-xl font-bold tracking-tight">Available Teachers</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          {candidates.length === 0
            ? 'No available teachers found for this slot.'
            : `${candidates.length} teacher${candidates.length !== 1 ? 's' : ''} available to cover this period`}
        </p>
      </div>

      {candidates.length === 0 && (
        <div className="bg-surface-elevated border border-border rounded-xl p-6 text-center text-text-secondary text-sm">
          All teachers are either absent, busy in another class, or already assigned a proxy for this period.
        </div>
      )}

      <div className="space-y-3">
        {sortedCandidates.map((candidate: any, i: number) => {
          const isFavorite = favoriteIds.has(candidate.teacher_id);
          return (
            <div
              key={candidate.teacher_id}
              style={{ animationDelay: `${Math.min(i, 6) * 40}ms` }}
              className={`bg-surface-elevated p-4 rounded-xl shadow-sm border transition-colors animate-slide-up ${
                candidate.is_recommended ? 'border-primary ring-1 ring-primary/15' : 'border-border'
              }`}
            >
              <div className="flex items-center gap-3 mb-3">
                <Avatar name={candidate.teacher_name} />
                <div className="flex-1 min-w-0">
                  <div className="font-bold truncate">{candidate.teacher_name}</div>
                  <div className="text-xs text-text-secondary truncate">
                    {candidate.is_recommended ? 'Recommended' : 'Available'}
                    {candidate.reasons?.length > 0 && ` · ${candidate.reasons.join(' · ')}`}
                  </div>
                </div>
                <button
                  aria-label={isFavorite ? `Remove ${candidate.teacher_name} from favorites` : `Add ${candidate.teacher_name} to favorites`}
                  onClick={() => favoriteMutation.mutate({ teacherId: candidate.teacher_id, isFavorite })}
                  className="min-h-[44px] min-w-[44px] flex items-center justify-center shrink-0 active:scale-90 transition-transform"
                >
                  <Heart size={19} className={isFavorite ? 'fill-warning text-warning' : 'text-text-muted'} />
                </button>
                {candidate.is_recommended && (
                  <span className="flex items-center gap-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded-full font-medium shrink-0">
                    <Sparkles size={12} /> Best fit
                  </span>
                )}
              </div>
              <Button
                className="w-full"
                variant={candidate.is_recommended ? 'primary' : 'ghost'}
                onClick={() => assignMutation.mutate(candidate.teacher_id)}
                disabled={assignMutation.isPending}
              >
                {assignMutation.isPending ? 'Assigning...' : 'Assign Proxy'}
              </Button>
            </div>
          );
        })}
      </div>

      {assignMutation.isError && (
        <div className="bg-error-bg border border-error/30 rounded-xl p-3 flex items-start gap-2 text-left animate-slide-up">
          <TriangleAlert size={16} className="text-error shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-error">
              {isCollision ? 'Availability changed' : "Couldn't save changes"}
            </p>
            <p className="text-xs text-error/80 mt-0.5">
              {assignErrorMessage ?? 'Your last action was not confirmed by the server. Please try again.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
