"""Catalogue des indicateurs : une seule source par indicateur pour tous les pays (comparabilité).

better : +1 si une valeur plus élevée est « mieux », -1 si plus basse est mieux,
         0 si l'indicateur est un repère de contexte (affiché, classé, mais hors score de synthèse).
Le sens retenu est affiché sur la page à côté de chaque indicateur.
"""

COUNTRIES = [  # (code page, nom, ISO3 Banque mondiale / FMI, code Eurostat)
    ("FR", "France", "FRA", "FR"),
    ("DE", "Allemagne", "DEU", "DE"),
    ("BE", "Belgique", "BEL", "BE"),
    ("LU", "Luxembourg", "LUX", "LU"),
    ("CH", "Suisse", "CHE", "CH"),
    ("IT", "Italie", "ITA", "IT"),
    ("ES", "Espagne", "ESP", "ES"),
    ("UK", "Royaume-Uni", "GBR", "UK"),
    ("NL", "Pays-Bas", "NLD", "NL"),
    ("SE", "Suède", "SWE", "SE"),
    ("DK", "Danemark", "DNK", "DK"),
    ("EU", "Moyenne UE", "EUU", "EU27_2020"),
]

DOMAINS = [
    ("edu", "Éducation"),
    ("eco", "Économie"),
    ("sante", "Santé"),
    ("social", "Social"),
    ("fisc", "Fiscalité"),
    ("eco2", "Écologie"),
    ("logement", "Logement"),
]

EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{code}?{params}"
WB = "https://api.worldbank.org/v2/country/{iso}/indicator/{code}?format=json&per_page=20000&date=2000:2026{extra}"
IMF = "https://www.imf.org/external/datamapper/api/v1/{code}"

# kind: eurostat | wb | imf | static
INDICATORS = [
    # ---------- Éducation ----------
    dict(id="pisa_math", domain="edu", label="PISA — mathématiques", unit="points", better=1, kind="static",
         note="Score moyen des élèves de 15 ans. 2006-2018 : Banque mondiale EdStats (LO.PISA.MAT) ; 2022 : OCDE, Résultats du PISA 2022, vol. I. Le Luxembourg n'a pas de score 2022 dans les tableaux consultés.",
         source="OCDE PISA / Banque mondiale EdStats (LO.PISA.MAT)"),
    dict(id="pisa_read", domain="edu", label="PISA — compréhension de l'écrit", unit="points", better=1, kind="static",
         note="Score moyen des élèves de 15 ans. 2006-2018 : Banque mondiale EdStats (LO.PISA.REA) ; 2022 : OCDE.",
         source="OCDE PISA / Banque mondiale EdStats (LO.PISA.REA)"),
    dict(id="early_leavers", domain="edu", label="Sorties précoces du système scolaire", unit="% des 18-24 ans", better=-1,
         kind="eurostat", code="sdg_04_10", params="sex=T&unit=PC&wstatus=POP&age=Y18-24",
         note="Jeunes de 18 à 24 ans sans diplôme du secondaire supérieur et hors formation.", source="Eurostat sdg_04_10"),
    dict(id="tertiary", domain="edu", label="Diplômés du supérieur", unit="% des 25-34 ans", better=1,
         kind="eurostat", code="edat_lfse_03", params="sex=T&age=Y25-34&isced11=ED5-8&unit=PC",
         note="CITE 5 à 8.", source="Eurostat edat_lfse_03"),
    dict(id="edu_spend", domain="edu", label="Dépense publique d'éducation", unit="% du PIB", better=0,
         kind="eurostat", code="gov_10a_exp", params="sector=S13&cofog99=GF09&na_item=TE&unit=PC_GDP",
         note="Dépenses des administrations publiques (fonction COFOG 09). Repère de contexte : dépenser plus n'est pas un résultat en soi.",
         source="Eurostat gov_10a_exp"),
    # ---------- Économie ----------
    dict(id="gdp_pc", domain="eco", label="PIB par habitant", unit="$ PPA constants 2021", better=1,
         kind="wb", code="NY.GDP.PCAP.PP.KD", note="Parité de pouvoir d'achat, dollars internationaux constants.",
         source="Banque mondiale NY.GDP.PCAP.PP.KD"),
    dict(id="growth", domain="eco", label="Croissance du PIB réel (moyenne sur 5 ans)", unit="% par an", better=1, kind="imf", code="NGDP_RPCH",
         note="FMI, Perspectives de l'économie mondiale ; moyenne glissante sur 5 ans (lisse les à-coups, dont 2020) ; années futures (projections) exclues.",
         source="FMI WEO NGDP_RPCH", avg5=True),
    dict(id="unemployment", domain="eco", label="Chômage", unit="% de la population active", better=-1,
         kind="wb", code="SL.UEM.TOTL.ZS", note="Estimation modélisée de l'OIT, harmonisée entre pays.",
         source="Banque mondiale / OIT SL.UEM.TOTL.ZS"),
    dict(id="youth_unemp", domain="eco", label="Chômage des 15-24 ans", unit="% de la population active", better=-1,
         kind="wb", code="SL.UEM.1524.ZS", note="Estimation modélisée de l'OIT.", source="Banque mondiale / OIT SL.UEM.1524.ZS"),
    dict(id="employment", domain="eco", label="Taux d'emploi des 20-64 ans", unit="%", better=1,
         kind="eurostat", code="lfsi_emp_a", params="age=Y20-64&sex=T&indic_em=EMP_LFS&unit=PC_POP",
         note="Enquête sur les forces de travail.", source="Eurostat lfsi_emp_a"),
    dict(id="debt", domain="eco", label="Dette publique", unit="% du PIB", better=-1, kind="imf", code="GGXWDG_NGDP",
         note="Dette brute des administrations publiques (FMI). Définition proche de Maastricht, pas identique.",
         source="FMI WEO GGXWDG_NGDP"),
    dict(id="deficit", domain="eco", label="Solde public", unit="% du PIB", better=1, kind="imf", code="GGXCNL_NGDP",
         note="Capacité (+) ou besoin (−) de financement des administrations publiques.", source="FMI WEO GGXCNL_NGDP"),
    # ---------- Santé ----------
    dict(id="life_exp", domain="sante", label="Espérance de vie à la naissance", unit="années", better=1,
         kind="wb", code="SP.DYN.LE00.IN", note="", source="Banque mondiale SP.DYN.LE00.IN"),
    dict(id="hly", domain="sante", label="Espérance de vie en bonne santé", unit="années", better=1,
         kind="eurostat", code="hlth_hlye", params="hlth_hle=HLY_Y0&sex=T&unit=YR",
         note="Années de vie sans limitation d'activité (enquête SILC) ; comparabilité imparfaite entre pays.",
         source="Eurostat hlth_hlye"),
    dict(id="avoidable", domain="sante", label="Mortalité évitable par les soins", unit="décès / 100 000 hab.", better=-1,
         kind="eurostat", code="hlth_cd_apr", params="sex=T&unit=RT&mortalit=TRT&icd10=TOTAL",
         note="Décès avant 75 ans qui auraient pu être évités par des soins de qualité en temps utile (« treatable »).",
         source="Eurostat hlth_cd_apr"),
    dict(id="health_spend", domain="sante", label="Dépense courante de santé par habitant", unit="$ PPA courants", better=0,
         kind="wb", code="SH.XPD.CHEX.PP.CD", note="Repère de contexte.", source="Banque mondiale / OMS SH.XPD.CHEX.PP.CD"),
    dict(id="oop", domain="sante", label="Reste à charge des ménages", unit="% de la dépense de santé", better=-1,
         kind="wb", code="SH.XPD.OOPC.CH.ZS", note="Paiements directs des ménages.", source="Banque mondiale / OMS SH.XPD.OOPC.CH.ZS"),
    dict(id="doctors", domain="sante", label="Médecins", unit="pour 1 000 hab.", better=1, kind="wb", code="SH.MED.PHYS.ZS",
         note="Définitions nationales hétérogènes (en exercice / habilités à exercer).", source="Banque mondiale / OMS SH.MED.PHYS.ZS"),
    # ---------- Social ----------
    dict(id="poverty", domain="social", label="Taux de pauvreté", unit="% de la population", better=-1,
         kind="eurostat", code="sdg_01_20", params="unit=PC",
         note="Revenu disponible inférieur à 60 % du revenu médian national (après transferts sociaux).",
         source="Eurostat sdg_01_20"),
    dict(id="arope", domain="social", label="Risque de pauvreté ou d'exclusion sociale", unit="% de la population", better=-1,
         kind="eurostat", code="ilc_peps01n", params="sex=T&age=TOTAL&unit=PC",
         note="Indicateur AROPE (pauvreté monétaire, privation sévère ou très faible intensité de travail).",
         source="Eurostat ilc_peps01n"),
    dict(id="gini", domain="social", label="Inégalités de revenus (Gini)", unit="0 à 100", better=-1,
         kind="eurostat", code="ilc_di12", params="age=TOTAL&statinfo=GINI_HND",
         note="Coefficient de Gini du revenu disponible équivalent.", source="Eurostat ilc_di12"),
    dict(id="emp_senior", domain="social", label="Taux d'emploi des 55-64 ans", unit="%", better=1,
         kind="eurostat", code="lfsi_emp_a", params="age=Y55-64&sex=T&indic_em=EMP_LFS&unit=PC_POP",
         note="Approche de la durée de vie active (l'âge effectif de sortie n'est pas publié de façon homogène en API).",
         source="Eurostat lfsi_emp_a"),
    # ---------- Fiscalité ----------
    dict(id="tax_burden", domain="fisc", label="Prélèvements obligatoires", unit="% du PIB", better=-1,
         kind="eurostat", code="gov_10a_taxag", params="na_item=D2_D5_D91_D61_M_D995&sector=S13_S212&unit=PC_GDP",
         note="Impôts et cotisations sociales effectives. Sens retenu : plus bas = mieux classé — choix discutable, une pression élevée finance aussi des services publics.",
         source="Eurostat gov_10a_taxag"),
    dict(id="tax_wedge", domain="fisc", label="Coin fiscal sur les bas salaires", unit="% du coût du travail", better=-1,
         kind="eurostat", code="earn_nt_taxwedge", params="unit=RT",
         note="Impôt sur le revenu + cotisations salariales et patronales, célibataire sans enfant à 67 % du salaire moyen.",
         source="Eurostat earn_nt_taxwedge"),
    dict(id="env_tax", domain="fisc", label="Fiscalité environnementale", unit="% du PIB", better=0,
         kind="eurostat", code="env_ac_tax", params="tax=ENV&unit=PC_GDP",
         note="Taxes sur l'énergie, les transports, la pollution et les ressources. Repère de contexte.",
         source="Eurostat env_ac_tax"),
    dict(id="gov_rev", domain="fisc", label="Recettes publiques totales", unit="% du PIB", better=0, kind="imf", code="rev",
         note="Toutes recettes des administrations publiques (FMI) ; couvre aussi la Suisse et le Royaume-Uni. Repère de contexte.",
         source="FMI Public Finances in Modern History / WEO (rev)"),
    # ---------- Écologie ----------
    dict(id="ghg_pc", domain="eco2", label="Émissions de gaz à effet de serre", unit="t éq. CO₂ par habitant", better=-1,
         kind="eurostat", code="sdg_13_10", params="src_crf=TOTXMEMO&unit=T_HAB",
         note="Émissions nettes hors aviation internationale (inventaires CCNUCC).", source="Eurostat sdg_13_10"),
    dict(id="renew", domain="eco2", label="Part des renouvelables", unit="% de la consommation finale brute d'énergie", better=1,
         kind="eurostat", code="nrg_ind_ren", params="nrg_bal=REN&unit=PC", note="", source="Eurostat nrg_ind_ren"),
    dict(id="carbon_elec", domain="eco2", label="Intensité carbone de l'électricité", unit="g CO₂ / kWh", better=-1, kind="owid",
         code="electricity-mix", url="https://ourworldindata.org/grapher/electricity-mix.csv?frequency=annual&metric=carbon_intensity&source=total&v=1&csvType=full&useColumnShortNames=true",
         note="Ember via Our World in Data (CC BY 4.0).", source="Ember / Our World in Data"),
    dict(id="recycling", domain="eco2", label="Recyclage des déchets municipaux", unit="%", better=1,
         kind="eurostat", code="cei_wm011", params="wst_oper=RCY&unit=PC", note="", source="Eurostat cei_wm011"),
    # ---------- Logement ----------
    dict(id="overburden", domain="logement", label="Surcharge des coûts du logement", unit="% de la population", better=-1,
         kind="eurostat", code="ilc_lvho07a", params="rskpovth=TOTAL&age=TOTAL&sex=T&unit=PC",
         note="Ménages dont les coûts du logement dépassent 40 % du revenu disponible.", source="Eurostat ilc_lvho07a"),
    dict(id="overcrowding", domain="logement", label="Surpeuplement", unit="% de la population", better=-1,
         kind="eurostat", code="ilc_lvho05a", params="rskpovth=TOTAL&age=TOTAL&sex=T&unit=PC", note="", source="Eurostat ilc_lvho05a"),
    dict(id="housing_depriv", domain="logement", label="Privation sévère liée au logement", unit="% de la population", better=-1,
         kind="eurostat", code="ilc_mdho06a", params="rskpovth=TOTAL&age=TOTAL&sex=T&unit=PC",
         note="Logement surpeuplé cumulé à au moins un problème grave (humidité, pas de sanitaires, trop sombre).",
         source="Eurostat ilc_mdho06a"),
    dict(id="owners", domain="logement", label="Propriétaires occupants", unit="% de la population", better=0,
         kind="eurostat", code="ilc_lvho02", params="rskpovth=TOTAL&hhcomp=TOTAL&tenure=OWN&unit=PC",
         note="Repère de contexte : la propriété n'est pas un objectif en soi (cf. Suisse, Allemagne).", source="Eurostat ilc_lvho02"),
    dict(id="house_prices", domain="logement", label="Prix des logements", unit="indice 2015 = 100", better=0,
         kind="eurostat", code="prc_hpi_a", params="purchase=TOTAL&unit=I15_A_AVG",
         note="Prix nominaux. Repère de contexte.", source="Eurostat prc_hpi_a"),
]

# Logement social : l'OCDE ne publie les valeurs exactes que dans le tableur de l'annexe ;
# on reprend les tranches du texte de l'indicateur PH4.2 (2022 ou dernière année).
SOCIAL_HOUSING = {
    "source": "OCDE, Affordable Housing Database, indicateur PH4.2 « Social rental housing stock » (2022 ou dernière année disponible)",
    "url": "https://www.oecd.org/content/dam/oecd/en/data/datasets/affordable-housing-database/ph4-2-social-rental-housing-stock.pdf",
    "bands": {
        "NL": "plus de 20 %", "DK": "plus de 20 %",
        "FR": "10 à 19 %", "UK": "10 à 19 %",
        "BE": "2 à 10 %", "DE": "2 à 10 %", "IT": "2 à 10 %", "CH": "2 à 10 %",
        "ES": "moins de 2 %",
        "SE": "hors définition (logement municipal à loyer de marché)",
        "LU": "non publié dans le texte de l'indicateur",
    },
    "note": "Hors panel : l'Autriche dépasse aussi 20 %. Moyenne OCDE : 7 % ; UE : 8 %.",
}

# PISA 2022 (OCDE, Résultats du PISA 2022, volume I, tableaux I.2.1 à I.2.3)
PISA_2022 = {
    "math": {"FR": 474, "DE": 475, "BE": 489, "CH": 508, "IT": 471, "ES": 473, "UK": 489, "NL": 493, "SE": 482, "DK": 489},
    "read": {"FR": 474, "DE": 480, "BE": 479, "CH": 483, "IT": 482, "ES": 474, "UK": 494, "NL": 459, "SE": 487, "DK": 489},
}
PISA_URL = "https://www.oecd.org/en/publications/pisa-2022-results-volume-i_53f23881-en.html"
