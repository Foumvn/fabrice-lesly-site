// Données des tables de l'événement (thème GLOIRE/ROYAL + RICHESSE/PROSPÉRITÉ)
export interface TableDef {
	name: string;
	subtitle: string;
	theme: string;
}

export const EVENT_TABLES: TableDef[] = [
	// Thème GLOIRE / ROYAL
	{ name: 'Table Apogée', subtitle: 'Le sommet', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Couronne', subtitle: 'Symbole royal', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Majesté', subtitle: 'Grandeur', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Triomphe', subtitle: 'Victoire', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Auréole', subtitle: 'Lumière divine', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Splendeur', subtitle: 'Éclat', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Renommée', subtitle: 'Réputation', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Laurier', subtitle: 'Couronne des vainqueurs', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Ovation', subtitle: 'Acclamations', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Rayonnement', subtitle: 'Briller', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Céleste', subtitle: "Gloire d'en haut", theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Magnificence', subtitle: 'Grandeur', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Panache', subtitle: 'Élégance + honneur', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Élévation', subtitle: 'Monter plus haut', theme: 'GLOIRE / ROYAL' },
	{ name: 'Table Exaltation', subtitle: 'Gloire + joie', theme: 'GLOIRE / ROYAL' },
	// Thème RICHESSE / PROSPÉRITÉ
	{ name: 'Table Opulence', subtitle: 'Abondance', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Abondance', subtitle: 'Rien ne manque', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Trésor', subtitle: 'Richesse cachée', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Fortune', subtitle: 'Chance + richesse', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Diamant', subtitle: 'Pierre précieuse', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Or Pur', subtitle: 'Valeur suprême', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Provision', subtitle: 'Tout est pourvu', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Jubilé', subtitle: 'Année de prospérité', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Bénédiction', subtitle: 'Gloire + prospérité', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Épanouissement', subtitle: 'Croître/fleurir', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Plénitude', subtitle: 'Complet, sans vide', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Héritage', subtitle: 'Richesse transmise', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Promo 14', subtitle: 'Confort, bien-être', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Promo 14', subtitle: 'Fruits du travail', theme: 'RICHESSE / PROSPÉRITÉ' },
	{ name: 'Table Jachin', subtitle: '"Il établira" - colonne du Temple', theme: 'RICHESSE / PROSPÉRITÉ' },
];

export const SEATS_PER_TABLE = 5;
