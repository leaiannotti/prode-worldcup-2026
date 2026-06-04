/**
 * Score formatting composable
 * Task 4.4: Format score_type enum to labels and point badge colors
 */

export interface ScoreDisplay {
  label: string
  color: string
}

/**
 * Format score type to human-readable label
 * exact → "Exacto" (3pts, green)
 * outcome → "Resultado" (1pt, amber)
 * miss → "Falló" (0pts, red)
 */
export function useScoreFormatter() {
  function formatScoreType(scoreType?: string): ScoreDisplay {
    switch (scoreType) {
      case 'exact':
        return {
          label: 'Exacto',
          color: 'bg-green-500'
        }
      case 'outcome':
        return {
          label: 'Resultado',
          color: 'bg-amber-500'
        }
      case 'miss':
        return {
          label: 'Falló',
          color: 'bg-red-500'
        }
      default:
        return {
          label: '—',
          color: 'bg-gray-400'
        }
    }
  }

  function pointsBadgeColor(points?: number): string {
    if (points === undefined || points === null) {
      return 'bg-gray-400'
    }
    switch (points) {
      case 3:
        return 'bg-green-500'
      case 1:
        return 'bg-amber-500'
      case 0:
        return 'bg-red-500'
      default:
        return 'bg-gray-400'
    }
  }

  function pointsLabel(points?: number): string {
    if (points === undefined || points === null) {
      return '—'
    }
    return `${points}pts`
  }

  return {
    formatScoreType,
    pointsBadgeColor,
    pointsLabel
  }
}
