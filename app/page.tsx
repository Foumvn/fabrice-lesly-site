import InfiniteGallery from '@/components/InfiniteGallery';

export default function Home() {
	const sampleImages = [
		{ src: '/321A6647.jpg.jpeg', alt: 'Photo 1' },
		{ src: '/321A6655.jpg.jpeg', alt: 'Photo 2' },
		{ src: '/321A6657.jpg.jpeg', alt: 'Photo 3' },
		{ src: '/321A6661.jpg.jpeg', alt: 'Photo 4' },
		{ src: '/321A6681.jpg.jpeg', alt: 'Photo 5' },
		{ src: '/321A6683.jpg.jpeg', alt: 'Photo 6' },
		{ src: '/321A6695.jpg.jpeg', alt: 'Photo 7' },
		{ src: '/321A6701.jpg.jpeg', alt: 'Photo 8' },
		{ src: '/321A6771.jpg.jpeg', alt: 'Photo 9' },
	];

	return (
		<main className="min-h-screen ">
			<InfiniteGallery
				images={sampleImages}
				speed={1.2}
				zSpacing={3}
				visibleCount={12}
				falloff={{ near: 0.8, far: 14 }}
				className="h-screen w-full rounded-lg overflow-hidden"
			/>
			<div className="fixed top-4 left-0 right-0 z-20 flex pointer-events-none items-start justify-center px-6">
				<img
					src="/anneaux.png"
					alt="Anneaux de mariage"
					className="w-36 sm:w-48 md:w-60 lg:w-64 drop-shadow-[0_0_30px_rgba(255,140,66,0.45)]"
				/>
			</div>
			<div className="h-screen inset-0 pointer-events-none fixed flex items-center justify-center text-center px-3 mix-blend-exclusion text-white">
				<h1 className="font-serif text-4xl md:text-7xl tracking-tight">
					<span className="italic">Fabrice et Leslie</span>
					<br />
					Amour et douceur
				</h1>
			</div>

			<div className="text-center fixed bottom-24 left-0 right-0 font-mono uppercase text-[11px] font-semibold">
				<p>Use mouse wheel, arrow keys, or touch to navigate</p>
				<p className=" opacity-60">
					Auto-play resumes after 3 seconds of inactivity
				</p>
			</div>
		</main>
	);
}
