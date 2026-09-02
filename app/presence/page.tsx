'use client';

import { useState } from 'react';

export default function PresencePage() {
	const [submitted, setSubmitted] = useState(false);
	const [name, setName] = useState('');
	const [confirmed, setConfirmed] = useState<'yes' | 'no' | ''>('');
	const [replacement, setReplacement] = useState<'yes' | 'no' | ''>('');
	const [replacementName, setReplacementName] = useState('');

	return (
		<main className="relative flex min-h-screen flex-col items-center justify-center bg-[#0a0a0a] px-6 pb-28 pt-16 text-white">
			<div className="w-full max-w-xl text-center">
				<div className="mb-6 inline-flex items-center justify-center rounded-full p-1.5"
					style={{
						background: 'linear-gradient(135deg, #ff8c42 0%, #ffb347 40%, #ff6a00 100%)',
						boxShadow: '0 0 40px rgba(255, 122, 16, 0.5), 0 10px 30px rgba(255, 106, 0, 0.35)',
					}}
				>
					<img
						src="/321A6647.jpg.jpeg"
						alt="Leslie & Fabrice"
						className="h-72 w-72 rounded-full object-cover sm:h-96 sm:w-96"
					/>
				</div>

				<img
					src="/anneaux.png"
					alt="Anneaux de mariage"
					className="mx-auto mb-5 w-24 opacity-80 sm:w-32"
				/>

				<h1 className="font-serif text-4xl md:text-5xl tracking-tight">
					Confirmer ma <span className="italic">présence</span>
				</h1>
				<p className="mt-3 font-mono text-xs uppercase tracking-widest text-white/50">
					Prestation photographique — réponse souhaitée
				</p>

				{!submitted ? (
					<form
						onSubmit={(e) => {
							e.preventDefault();
							setSubmitted(true);
						}}
						className="mt-10 space-y-5 text-left"
					>
						<div>
							<label className="mb-2 block font-mono text-[11px] uppercase tracking-widest text-white/50">
								Nom &amp; prénom
							</label>
							<input
								type="text"
								required
								value={name}
								onChange={(e) => setName(e.target.value)}
								placeholder="Votre nom complet"
								className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/30 backdrop-blur-xl outline-none transition focus:border-white/30"
							/>
						</div>

						<div>
							<label className="mb-2 block font-mono text-[11px] uppercase tracking-widest text-white/50">
								Serez-vous remplacé&nbsp;?
							</label>
							<div className="grid grid-cols-2 gap-3">
								<button
									type="button"
									onClick={() => setReplacement('yes')}
									className={`rounded-2xl border px-4 py-3 transition active:scale-[0.98] ${
										replacement === 'yes'
											? 'border-orange-400 bg-orange-500/40 text-white shadow-[0_0_20px_rgba(255,140,66,0.4)]'
											: 'border-white/10 bg-white/5 text-white/60 hover:bg-white/10 active:bg-orange-500/60'
									}`}
								>
									Oui
								</button>
								<button
									type="button"
									onClick={() => {
										setReplacement('no');
										setReplacementName('');
									}}
									className={`rounded-2xl border px-4 py-3 transition active:scale-[0.98] ${
										replacement === 'no'
											? 'border-orange-400 bg-orange-500/40 text-white shadow-[0_0_20px_rgba(255,140,66,0.4)]'
											: 'border-white/10 bg-white/5 text-white/60 hover:bg-white/10 active:bg-orange-500/60'
									}`}
								>
									Non
								</button>
							</div>
							{replacement === 'yes' && (
								<input
									type="text"
									required
									value={replacementName}
									onChange={(e) => setReplacementName(e.target.value)}
									placeholder="Nom de la personne qui vous remplace"
									className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/30 backdrop-blur-xl outline-none transition focus:border-white/30"
								/>
							)}
						</div>

						<div>
							<label className="mb-2 block font-mono text-[11px] uppercase tracking-widest text-white/50">
								Serez-vous présent&nbsp;?
							</label>
							<div className="grid grid-cols-2 gap-3">
								<button
									type="button"
									onClick={() => setConfirmed('yes')}
									className={`rounded-2xl border px-4 py-3 transition active:scale-[0.98] ${
										confirmed === 'yes'
											? 'border-orange-400 bg-orange-500/40 text-white shadow-[0_0_20px_rgba(255,140,66,0.4)]'
											: 'border-white/10 bg-white/5 text-white/60 hover:bg-white/10 active:bg-orange-500/60'
									}`}
								>
									Oui, présent
								</button>
								<button
									type="button"
									onClick={() => setConfirmed('no')}
									className={`rounded-2xl border px-4 py-3 transition active:scale-[0.98] ${
										confirmed === 'no'
											? 'border-orange-400 bg-orange-500/40 text-white shadow-[0_0_20px_rgba(255,140,66,0.4)]'
											: 'border-white/10 bg-white/5 text-white/60 hover:bg-white/10 active:bg-orange-500/60'
									}`}
								>
									Non, absent
								</button>
							</div>
						</div>

						<button
							type="submit"
							disabled={!confirmed}
							className="w-full rounded-full border border-white/15 bg-white/10 py-4 font-mono text-sm uppercase tracking-widest text-white backdrop-blur-xl transition hover:bg-white/20 active:scale-[0.98] active:bg-orange-500 active:shadow-[0_0_30px_rgba(255,140,66,0.5)] disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100 disabled:active:bg-white/10"
						>
							Envoyer ma confirmation
						</button>
					</form>
				) : (
					<div className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
						<div className="text-4xl">✓</div>
						<p className="mt-3 font-serif text-2xl">
							Merci{name ? `, ${name}` : ''}&nbsp;!
						</p>
						<p className="mt-2 text-sm text-white/60">
							{confirmed === 'yes'
								? 'Votre présence est confirmée. Nous avons hâte de vous voir.'
								: 'Merci de nous avoir informé. Vous nous manquerez.'}
							{replacement === 'yes' && replacementName
								? ` ${replacementName} vous remplacera.`
								: ''}
						</p>
						<button
							type="button"
							onClick={() => {
								setSubmitted(false);
								setName('');
								setConfirmed('');
								setReplacement('');
								setReplacementName('');
							}}
							className="mt-6 rounded-full border border-white/15 bg-white/10 px-6 py-2.5 font-mono text-xs uppercase tracking-widest transition hover:bg-white/20 active:scale-[0.98] active:bg-orange-500"
						>
							Modifier ma réponse
						</button>
					</div>
				)}
			</div>
		</main>
	);
}