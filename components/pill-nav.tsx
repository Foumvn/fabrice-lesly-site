'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { User, Bell, Camera, Home } from 'lucide-react';

const ITEMS = [
	{ href: '/presence', label: 'Confirmer ma présence', icon: User },
	{ href: '/programme', label: 'Voir le programme', icon: Bell },
	{ href: '/gallery', label: 'Gallery', icon: Camera },
	{ href: '/', label: 'Accueil', icon: Home },
];

export default function PillNav() {
	const pathname = usePathname();

	return (
		<div className="pointer-events-none fixed inset-x-0 bottom-5 z-30 flex justify-center">
			<nav className="pointer-events-auto relative flex h-14 items-center gap-2 rounded-full border border-white/15 bg-white/10 p-2 shadow-[0_8px_32px_rgba(0,0,0,0.35)] backdrop-blur-2xl">
				{ITEMS.map(({ href, label, icon: Icon }) => {
					const active = pathname === href;
					return (
						<Link
							key={href}
							href={href}
							className="group relative flex items-center justify-center"
						>
							<span className="pointer-events-none absolute -top-11 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-xl border border-white/10 bg-black/70 px-3 py-1.5 text-xs font-mono uppercase tracking-wide text-white opacity-0 shadow-lg backdrop-blur-xl transition-opacity duration-200 group-hover:opacity-100">
								{label}
							</span>
							<span
								className={`flex h-11 w-11 items-center justify-center rounded-3xl border transition-all duration-200 active:scale-90 active:bg-orange-500 active:border-orange-400 active:text-white active:shadow-[0_0_20px_rgba(255,140,66,0.5)] ${
									active
										? 'border-white/30 bg-white text-black shadow'
										: 'border-white/15 bg-white/80 text-black hover:bg-white'
								}`}
							>
								<Icon className="h-6 w-6" strokeWidth={1.5} />
							</span>
						</Link>
					);
				})}
			</nav>
		</div>
	);
}
