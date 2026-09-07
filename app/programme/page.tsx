'use client';

import { Bell } from 'lucide-react';

const PROGRAM = [
	{ time: '14h00', title: 'Accueil & remise des dépliants', desc: 'Café de bienvenue et retrouvailles' },
	{ time: '15h30', title: 'Séance photo officielle', desc: 'Prises de vues du groupe, familles et amis' },
	{ time: '17h00', title: 'Pause goûter', desc: 'Buffet sucré et boissons' },
	{ time: '18h30', title: 'Cocktail & échanges', desc: 'Moments libres, photos spontanées' },
	{ time: '20h00', title: 'Soirée & clôture', desc: 'Animation, remerciements et dernières photos' },
];

export default function ProgramPage() {
	return (
		<main className="relative flex min-h-screen flex-col items-center justify-center bg-[#0a0a0a] px-6 py-20 text-white">
			<div className="w-full max-w-2xl text-center">
				<div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-3xl border border-white/10 bg-white/90 text-black shadow-lg">
					<Bell className="h-8 w-8" strokeWidth={1.5} />
				</div>

				<h1 className="font-serif text-4xl md:text-5xl tracking-tight">
					Le <span className="italic">programme</span>
				</h1>
				<p className="mt-3 font-mono text-xs uppercase tracking-widest text-white/50">
					Photographies &amp; animation de la journée
				</p>

				<ol className="mt-12 space-y-4 text-left">
					{PROGRAM.map((item) => (
						<li
							key={item.time}
							className="flex items-start gap-5 rounded-3xl border border-white/10 bg-white/5 px-6 py-5 backdrop-blur-xl"
						>
							<span className="mt-0.5 min-w-[4.5rem] font-mono text-sm font-semibold text-white/50">
								{item.time}
							</span>
							<div>
								<p className="font-serif text-lg">{item.title}</p>
								<p className="mt-1 text-sm text-white/60">{item.desc}</p>
							</div>
						</li>
					))}
				</ol>
			</div>
		</main>
	);
}