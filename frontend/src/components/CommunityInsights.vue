<template>
  <section class="bg-surface-container-low rounded-2xl p-5">
    <h2 class="font-headline-md text-headline-md text-on-surface mb-4">
      {{ t('communityInsights.title') }}
    </h2>

    <!-- Loading -->
    <div v-if="loading" class="space-y-5">
      <div v-for="i in 3" :key="i" class="space-y-2">
        <div class="h-4 w-40 bg-surface-container animate-pulse rounded" />
        <div class="h-7 w-full bg-surface-container animate-pulse rounded-full" />
      </div>
    </div>

    <!-- Error -->
    <p v-else-if="error" class="text-sm text-error">{{ t('communityInsights.error') }}</p>

    <!-- Empty -->
    <p v-else-if="items.length === 0" class="text-sm text-on-surface-variant">
      {{ t('communityInsights.noMatches') }}
    </p>

    <!-- Items -->
    <div v-else class="space-y-5">
      <div v-for="item in items" :key="item.match_id">
        <!-- Match header -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <img v-if="item.home_team.flag_url" :src="item.home_team.flag_url" class="w-5 h-4 object-cover rounded-sm" />
            <span class="font-label-md text-sm text-on-surface">{{ item.home_team.code }}</span>
            <span class="text-xs text-on-surface-variant font-body-md">vs</span>
            <img v-if="item.away_team.flag_url" :src="item.away_team.flag_url" class="w-5 h-4 object-cover rounded-sm" />
            <span class="font-label-md text-sm text-on-surface">{{ item.away_team.code }}</span>
          </div>
          <span class="text-xs text-on-surface-variant font-body-md">
            {{ item.has_data ? t('communityInsights.votes', { n: item.total_predictions }) : '' }}
          </span>
        </div>

        <!-- No data -->
        <div v-if="!item.has_data" class="flex items-center justify-center h-7 rounded-full border-2 border-dashed border-outline-variant">
          <span class="text-xs text-on-surface-variant font-label-sm uppercase tracking-wider">Sin predicciones aún</span>
        </div>

        <!-- Bar -->
        <div v-else>
          <div class="flex h-8 rounded-xl overflow-hidden gap-px">
            <!-- Home win — siempre visible, min 8px si hay data -->
            <div
              class="flex items-center justify-center gap-1 text-[11px] font-bold transition-all overflow-hidden"
              :style="{
                width: item.home_win_pct > 0 ? item.home_win_pct + '%' : '0%',
                minWidth: item.home_win_pct > 0 ? '8px' : '0',
                background: 'var(--color-primary)',
                color: 'var(--color-on-primary)',
              }"
            >
              <template v-if="item.home_win_pct >= 20">
                <span class="truncate">{{ item.home_team.code }}</span>
                <span>{{ item.home_win_pct }}%</span>
              </template>
              <span v-else-if="item.home_win_pct >= 10">{{ item.home_win_pct }}%</span>
            </div>
            <!-- Draw -->
            <div
              class="flex items-center justify-center gap-1 text-[11px] font-bold transition-all overflow-hidden"
              :style="{
                width: item.draw_pct > 0 ? item.draw_pct + '%' : '0%',
                minWidth: item.draw_pct > 0 ? '8px' : '0',
                background: 'var(--color-outline)',
                color: 'white',
              }"
            >
              <template v-if="item.draw_pct >= 20">
                <span>Emp.</span>
                <span>{{ item.draw_pct }}%</span>
              </template>
              <span v-else-if="item.draw_pct >= 10">{{ item.draw_pct }}%</span>
            </div>
            <!-- Away win -->
            <div
              class="flex items-center justify-center gap-1 text-[11px] font-bold transition-all overflow-hidden"
              :style="{
                width: item.away_win_pct > 0 ? item.away_win_pct + '%' : '0%',
                minWidth: item.away_win_pct > 0 ? '8px' : '0',
                background: 'var(--color-secondary)',
                color: 'var(--color-on-secondary)',
              }"
            >
              <template v-if="item.away_win_pct >= 20">
                <span class="truncate">{{ item.away_team.code }}</span>
                <span>{{ item.away_win_pct }}%</span>
              </template>
              <span v-else-if="item.away_win_pct >= 10">{{ item.away_win_pct }}%</span>
            </div>
          </div>

          <!-- Labels siempre visibles debajo -->
          <div class="flex justify-between mt-1.5 text-[11px] font-body-md">
            <span class="text-primary font-bold">{{ item.home_team.code }} {{ item.home_win_pct }}%</span>
            <span class="text-on-surface-variant">{{ t('communityInsights.draw') }} {{ item.draw_pct }}%</span>
            <span class="text-secondary font-bold">{{ item.away_team.code }} {{ item.away_win_pct }}%</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface InsightItem {
  match_id: number
  home_team: { code: string; name: string; flag_url: string }
  away_team: { code: string; name: string; flag_url: string }
  kickoff_at: string
  has_data: boolean
  total_predictions: number
  home_win_pct?: number
  draw_pct?: number
  away_win_pct?: number
}

const items = ref<InsightItem[]>([])
const loading = ref(true)
const error = ref(false)

async function fetchInsights() {
  loading.value = true
  error.value = false
  try {
    const res = await fetch('/api/matches/community-insights?limit=6', {
      credentials: 'include',
    })
    if (!res.ok) throw new Error()
    items.value = await res.json()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(fetchInsights)

defineExpose({ refresh: fetchInsights })
</script>
