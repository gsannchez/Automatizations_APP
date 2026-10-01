/** Tipos de producción alineados con backend: pipeline IA y ViralStyle */

export type ProductionCategory = 'ai_short';

export interface ProductionType {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: ProductionCategory;
  /** Orden en UI (menor = primero) */
  sort_order: number;
  route: string;
  queryParams?: Record<string, string>;
  viralStyleId?: string;
  platform?: 'TIKTOK' | 'REELS' | 'SHORTS';
  featured?: boolean;
  tags: string[];
}

export const PRODUCTION_TYPES: ProductionType[] = [
  {
    id: 'cctv',
    name: 'CCTV / Vigilancia',
    description: 'Footage estilo cámara de seguridad con timestamp y grano.',
    icon: '📹',
    category: 'ai_short',
    sort_order: 10,
    route: '/videos/new',
    queryParams: { format: 'cctv', style: 'cctv', platform: 'TIKTOK' },
    viralStyleId: 'cctv',
    platform: 'TIKTOK',
    featured: true,
    tags: ['CCTV', 'True crime'],
  },
  {
    id: 'dashcam',
    name: 'Dashcam',
    description: 'Cámara de coche, vibración de carretera y estética dashcam viral.',
    icon: '🚗',
    category: 'ai_short',
    sort_order: 20,
    route: '/videos/new',
    queryParams: { format: 'dashcam', style: 'dashcam', platform: 'TIKTOK' },
    viralStyleId: 'dashcam',
    platform: 'TIKTOK',
    tags: ['Dashcam'],
  },
  {
    id: 'bodycam',
    name: 'Bodycam / Policía',
    description: 'Estilo bodycam con gran angular, shake y filtros de cámara corporal.',
    icon: '🚔',
    category: 'ai_short',
    sort_order: 30,
    route: '/videos/new',
    queryParams: { format: 'bodycam', style: 'bodycam', platform: 'TIKTOK' },
    viralStyleId: 'bodycam',
    platform: 'TIKTOK',
    tags: ['Bodycam', 'Viral'],
  },
  {
    id: 'horror',
    name: 'Horror / Creepypasta',
    description: 'Atmósfera found-footage, night vision y narración de terror.',
    icon: '👻',
    category: 'ai_short',
    sort_order: 40,
    route: '/videos/new',
    queryParams: { format: 'horror', style: 'horror', platform: 'TIKTOK' },
    viralStyleId: 'horror',
    platform: 'TIKTOK',
    tags: ['Horror'],
  },
  {
    id: 'news',
    name: 'Noticias virales',
    description: 'Breaking news con ritmo rápido y subtítulos estilo TV.',
    icon: '📰',
    category: 'ai_short',
    sort_order: 50,
    route: '/videos/new',
    queryParams: { format: 'news', style: 'news', platform: 'TIKTOK' },
    viralStyleId: 'news',
    platform: 'TIKTOK',
    tags: ['News'],
  },
  {
    id: 'documentary',
    name: 'Documental',
    description: 'Realismo documental, grano de película y narración sobria.',
    icon: '🌍',
    category: 'ai_short',
    sort_order: 60,
    route: '/videos/new',
    queryParams: { format: 'documentary', style: 'documentary', platform: 'SHORTS' },
    viralStyleId: 'documentary',
    platform: 'SHORTS',
    tags: ['Documental'],
  },
  {
    id: 'meme',
    name: 'Meme realism',
    description: 'Estética meme candid con cortes bruscos y colores intensos.',
    icon: '😂',
    category: 'ai_short',
    sort_order: 70,
    route: '/videos/new',
    queryParams: { format: 'meme', style: 'meme_realism', platform: 'TIKTOK' },
    viralStyleId: 'meme_realism',
    platform: 'TIKTOK',
    tags: ['Meme'],
  },
  {
    id: 'anime_amv',
    name: 'Anime AMV',
    description: 'Edición anime con colores saturados, transiciones whip y phonk.',
    icon: '✨',
    category: 'ai_short',
    sort_order: 80,
    route: '/videos/new',
    queryParams: { format: 'anime', style: 'anime_edit', platform: 'TIKTOK' },
    viralStyleId: 'anime_edit',
    platform: 'TIKTOK',
    tags: ['Anime', 'AMV'],
  },
  {
    id: 'movie_recap',
    name: 'Resumen cinematográfico',
    description: 'IA genera guion estilo recap de película con look cinematográfico épico.',
    icon: '🎞',
    category: 'ai_short',
    sort_order: 90,
    route: '/videos/new',
    queryParams: {
      format: 'movie_recap',
      platform: 'TIKTOK',
      style: 'cinematic',
      topic: 'Resumen cinematográfico de la película',
    },
    viralStyleId: 'cinematic',
    platform: 'TIKTOK',
    featured: true,
    tags: ['Recap', 'Cine'],
  },
  {
    id: 'ai_short_tiktok',
    name: 'Short IA · TikTok',
    description: 'Guion con IA, imágenes SDXL/ComfyUI, voz ElevenLabs y montaje vertical 9:16.',
    icon: '♪',
    category: 'ai_short',
    sort_order: 100,
    route: '/videos/new',
    queryParams: { format: 'ai_short', platform: 'TIKTOK', style: 'tiktok_native' },
    viralStyleId: 'tiktok_native',
    platform: 'TIKTOK',
    featured: true,
    tags: ['IA', 'Vertical', 'Viral'],
  },
  {
    id: 'ai_short_reels',
    name: 'Short IA · Reels',
    description: 'Mismo pipeline Audio-First optimizado para Instagram Reels.',
    icon: '📸',
    category: 'ai_short',
    sort_order: 110,
    route: '/videos/new',
    queryParams: { format: 'ai_short', platform: 'REELS', style: 'cinematic' },
    viralStyleId: 'cinematic',
    platform: 'REELS',
    tags: ['IA', 'Reels'],
  },
  {
    id: 'ai_short_shorts',
    name: 'Short IA · YouTube Shorts',
    description: 'Vídeos cortos para YouTube con timeline y render FFmpeg.',
    icon: '▶',
    category: 'ai_short',
    sort_order: 120,
    route: '/videos/new',
    queryParams: { format: 'ai_short', platform: 'SHORTS', style: 'cinematic_ai' },
    viralStyleId: 'cinematic_ai',
    platform: 'SHORTS',
    tags: ['IA', 'Shorts'],
  },
  {
    id: 'cinematic_ai',
    name: 'Cinematic AI',
    description: 'Hiperrealismo IA, iluminación ray-traced y banda sonora épica.',
    icon: '🌅',
    category: 'ai_short',
    sort_order: 130,
    route: '/videos/new',
    queryParams: { format: 'cinematic_ai', style: 'cinematic_ai', platform: 'REELS' },
    viralStyleId: 'cinematic_ai',
    platform: 'REELS',
    tags: ['8K', 'IA'],
  },
];

export function sortProductionTypes(types: ProductionType[]): ProductionType[] {
  return [...types].sort((a, b) => a.name.localeCompare(b.name, 'es', { sensitivity: 'base' }));
}

export function getProductionType(id: string): ProductionType | undefined {
  return PRODUCTION_TYPES.find((p) => p.id === id);
}

export function getProductionTypesByCategory(category: ProductionCategory): ProductionType[] {
  return sortProductionTypes(PRODUCTION_TYPES.filter((p) => p.category === category));
}

export function getFeaturedProductionTypes(): ProductionType[] {
  return sortProductionTypes(PRODUCTION_TYPES.filter((p) => p.featured));
}
