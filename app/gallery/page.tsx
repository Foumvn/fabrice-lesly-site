'use client';

import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

const EASE = [0.16, 1, 0.3, 1] as const;

interface StackGroup {
	title: string;
	caption: string;
	photos: { src: string; alt: string }[];
}

const STACKS: StackGroup[] = [
	{
		title: 'Le grand jour',
		caption: 'Nos premières émotions',
		photos: [
			{ src: '/321A6647.jpg.jpeg', alt: 'Le grand jour 1' },
			{ src: '/321A6655.jpg.jpeg', alt: 'Le grand jour 2' },
			{ src: '/321A6657.jpg.jpeg', alt: 'Le grand jour 3' },
			{ src: '/321A6661.jpg.jpeg', alt: 'Le grand jour 4' },
		],
	},
	{
		title: 'Nos sourires',
		caption: 'Des instants complices',
		photos: [
			{ src: '/321A6681.jpg.jpeg', alt: 'Nos sourires 1' },
			{ src: '/321A6683.jpg.jpeg', alt: 'Nos sourires 2' },
			{ src: '/321A6695.jpg.jpeg', alt: 'Nos sourires 3' },
			{ src: '/321A6701.jpg.jpeg', alt: 'Nos sourires 4' },
		],
	},
	{
		title: 'Amour et douceur',
		caption: 'Notre histoire à jamais',
		photos: [
			{ src: '/321A6647.jpg.jpeg', alt: 'Amour et douceur 1' },
			{ src: '/321A6771.jpg.jpeg', alt: 'Amour et douceur 2' },
			{ src: '/321A6683.jpg.jpeg', alt: 'Amour et douceur 3' },
			{ src: '/321A6701.jpg.jpeg', alt: 'Amour et douceur 4' },
		],
	},
	{
		title: 'Ensemble pour toujours',
		caption: 'Chaque instant compte',
		photos: [
			{ src: '/321A6661.jpg.jpeg', alt: 'Ensemble 1' },
			{ src: '/321A6695.jpg.jpeg', alt: 'Ensemble 2' },
			{ src: '/321A6657.jpg.jpeg', alt: 'Ensemble 3' },
			{ src: '/321A6681.jpg.jpeg', alt: 'Ensemble 4' },
		],
	},
];

function StackCard({
	group,
	index,
	onOpen,
}: {
	group: StackGroup;
	index: number;
	onOpen: () => void;
}) {
	const [isHovered, setIsHovered] = useState(false);

	return (
		<motion.div
			layout
			initial={{ opacity: 0, scale: 0.95, y: 10 }}
			animate={{ opacity: 1, scale: 1, y: 0 }}
			transition={{
				duration: 0.25,
				delay: Math.min(index * 0.05, 0.3),
				ease: EASE,
				layout: { duration: 0.25, ease: EASE },
			}}
			className="relative"
			style={{
				perspective: '1200px',
				zIndex: isHovered ? 50 : 1,
				transformStyle: 'preserve-3d',
			}}
			onMouseEnter={() => setIsHovered(true)}
			onMouseLeave={() => setIsHovered(false)}
			onClick={onOpen}
		>
			<div className="relative w-[288px] cursor-pointer transition-all duration-150 active:scale-[0.97] active:ring-4 active:ring-orange-400/70 active:rounded-2xl active:shadow-[0_0_30px_rgba(255,140,66,0.6)]">
				{/* Back panel with stacked photos */}
				<motion.div
					className="relative z-0 rounded-2xl overflow-hidden"
					animate={{ rotateX: isHovered ? 15 : 0 }}
					transition={{ type: 'spring', stiffness: 200, damping: 25, mass: 0.8 }}
					style={{
						height: '224px',
						background: '#1e1e1e',
						border: '1px solid rgba(255, 255, 255, 0.06)',
						transformStyle: 'preserve-3d',
						transformOrigin: 'center bottom',
					}}
				>
					{group.photos.map((photo, i) => {
						const centerIndex = Math.floor(group.photos.length / 2);
						const dist = Math.abs(i - centerIndex);
						const scatter = [
							{ x: -46, y: 10, r: -8 },
							{ x: -15, y: 0, r: -3 },
							{ x: 16, y: 2, r: 3 },
							{ x: 46, y: 10, r: 8 },
						];
						const base = scatter[Math.min(i, 3)] || scatter[0];
						const pos = {
							x: base.x + (isHovered ? base.x * 0.4 : 0),
							y: base.y + (isHovered ? -8 : 0),
							r: base.r,
						};
						const z = 10 - dist;
						const brightness = dist === 0 ? 1 : dist === 1 ? 0.6 : 0.35;
						const blur = dist === 0 ? 0 : dist === 1 ? 0.5 : 1.5;

						return (
							<motion.div
								key={i}
								className="absolute left-1/2 top-0"
								initial={false}
								animate={{
									x: `calc(-50% + ${pos.x}px)`,
									y: pos.y,
									rotate: pos.r,
								}}
								transition={{
									type: 'spring',
									stiffness: 100,
									damping: 16,
									mass: 1,
								}}
								style={{ zIndex: z }}
							>
								<div
									className="h-[168px] w-[104px] overflow-hidden rounded-lg"
									style={{
										filter: `brightness(${brightness}) blur(${blur}px)`,
									}}
								>
									<img src={photo.src} alt={photo.alt} className="h-full w-full object-cover" />
								</div>
							</motion.div>
						);
					})}
					<div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-inset ring-white/10" />
				</motion.div>

				{/* Front panel */}
				<motion.div
					className="absolute bottom-0 left-0 right-0 z-10 rounded-2xl overflow-hidden"
					animate={{ rotateX: isHovered ? -25 : 0 }}
					transition={{ type: 'spring', stiffness: 180, damping: 22, mass: 0.8 }}
					style={{
						backdropFilter: 'blur(16px)',
						WebkitBackdropFilter: 'blur(16px)',
						background: 'rgba(26, 26, 26, 0.8)',
						border: '1px solid rgba(255, 255, 255, 0.06)',
						transformStyle: 'preserve-3d',
						transformOrigin: 'center bottom',
					}}
				>
					<div className="relative py-4 px-4">
						<h3 className="font-serif text-base leading-snug text-white/70 transition-colors duration-200">
							{group.title}
						</h3>
					</div>
					<div className="relative h-[48px]">
						<div className="absolute inset-x-0 top-0 h-[1px] bg-white/[0.04]" />
						<div className="relative h-full flex items-center justify-between px-4">
							<span className="text-[13px] text-white/60">{group.caption}</span>
							<span className="font-mono text-[11px] uppercase tracking-widest text-white/40">
								{group.photos.length} clichés
							</span>
						</div>
					</div>
				</motion.div>
			</div>
		</motion.div>
	);
}

export default function GalleryPage() {
	const [active, setActive] = useState<{ group: number; photo: number } | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const [showContent, setShowContent] = useState(false);

	useEffect(() => {
		const t = setTimeout(() => setIsLoading(false), 1200);
		return () => clearTimeout(t);
	}, []);

	useEffect(() => {
		if (!isLoading) {
			const t = setTimeout(() => setShowContent(true), 200);
			return () => clearTimeout(t);
		}
	}, [isLoading]);

	return (
		<div className="min-h-screen bg-[#191919] pb-28">
			<div
				className="transition-all duration-700 ease-out"
				style={{
					opacity: showContent ? 1 : 0,
					transform: showContent ? 'translateY(0)' : 'translateY(12px)',
				}}
			>
				<main
					className="mx-auto w-full px-4 pt-12 sm:px-6 sm:pt-14 md:px-8 md:pt-16"
					style={{ maxWidth: '912px' }}
				>
					<div className="mb-10 text-center">
						<p className="font-mono text-[11px] uppercase tracking-widest text-white/50">
							Fabrice &amp; Leslie
						</p>
						<h1 className="mt-2 font-serif text-3xl sm:text-4xl tracking-tight text-white">
							Nos <span className="italic">souvenirs</span>
						</h1>
					</div>

					<div
						className="mx-auto"
						style={{
							display: 'grid',
							gridTemplateColumns: 'repeat(auto-fit, 288px)',
							gap: '24px',
							justifyContent: 'center',
							width: '100%',
						}}
					>
						{STACKS.map((group, idx) => (
							<StackCard
								key={group.title}
								group={group}
								index={idx}
								onOpen={() => setActive({ group: idx, photo: 0 })}
							/>
						))}
					</div>
				</main>
			</div>

			{/* Lightbox */}
			{active !== null && (
				<div
					className="fixed inset-0 z-40 flex items-center justify-center bg-black/90 px-6 backdrop-blur-xl"
					onClick={() => setActive(null)}
				>
					<button
						className="absolute top-6 right-6 flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-white/10 text-white transition hover:bg-white/20"
						onClick={() => setActive(null)}
						aria-label="Fermer"
					>
						<X className="h-5 w-5" strokeWidth={1.5} />
					</button>

					{STACKS[active.group].photos.length > 1 && (
						<>
							<button
								className="absolute left-4 flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-white/10 text-white transition hover:bg-white/20"
								onClick={(e) => {
									e.stopPropagation();
									setActive((prev) => {
										if (!prev) return prev;
										const n = STACKS[prev.group].photos.length;
										return { ...prev, photo: (prev.photo - 1 + n) % n };
									});
								}}
								aria-label="Précédent"
							>
								<ChevronLeft className="h-5 w-5" strokeWidth={1.5} />
							</button>
							<button
								className="absolute right-4 flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-white/10 text-white transition hover:bg-white/20"
								onClick={(e) => {
									e.stopPropagation();
									setActive((prev) => {
										if (!prev) return prev;
										const n = STACKS[prev.group].photos.length;
										return { ...prev, photo: (prev.photo + 1) % n };
									});
								}}
								aria-label="Suivant"
							>
								<ChevronRight className="h-5 w-5" strokeWidth={1.5} />
							</button>
						</>
					)}

					<motion.img
						key={active.photo}
						src={STACKS[active.group].photos[active.photo].src}
						alt={STACKS[active.group].photos[active.photo].alt}
						initial={{ opacity: 0, scale: 0.96 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ duration: 0.3, ease: EASE }}
						className="max-h-[80vh] max-w-[92vw] rounded-2xl object-contain shadow-2xl"
						onClick={(e) => e.stopPropagation()}
					/>
					<div className="absolute bottom-6 left-0 right-0 flex flex-col items-center gap-1 px-4">
						<p className="font-serif text-lg text-white/80">{STACKS[active.group].title}</p>
						<p className="font-mono text-[11px] uppercase tracking-widest text-white/50">
							{active.photo + 1} / {STACKS[active.group].photos.length}
						</p>
					</div>
				</div>
			)}
		</div>
	);
}
