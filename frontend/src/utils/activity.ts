import type { ActivityEvent } from '@/stores/activity'

export function formatPrizeChangedEvent(event: ActivityEvent, t: any): string {
  const p = event.payload || {}
  const actor = p.actor_name || t('activity.someone')
  const admin = p.actor_is_admin ? ` ${t('activity.adminMarker')}` : ''
  const rank =
    p.rank === 1
      ? t('leagueDetail.prizeRankFirst')
      : p.rank === 2
        ? t('leagueDetail.prizeRankSecond')
        : t('leagueDetail.prizeRankThird')
  return t('activity.prizeChanged', {
    user: `${actor}${admin}`,
    rank,
    previous: p.previous_value || '',
    new: p.new_value || '',
  })
}
