import datetime
from typing import List, Union

from langchain_core.pydantic_v1 import BaseModel, Field


class TacheEntreprise(BaseModel):
    tache: str = Field(
        description="Tâche ou réalisation ou activité réalisée dans l'entreprise."
    )


class StackTechnique(BaseModel):
    tache: str = Field(
        description="Elément de l'environnement technique de la mission, à savoir : une méthodologie, un outil, une technologie, un langage de programmation ou une plateforme de développement et de travail."
    )


class CompetenceAcquiseDiplome(BaseModel):
    tache: str = Field(
        description="Compétence acquise au cours de la formation diplomante, si mentionnée."
    )


class CompetenceAcquiseCertification(BaseModel):
    tache: str = Field(
        description="Compétence acquise au cours de la certification, si mentionnée."
    )


class EntrepriseExperience(BaseModel):
    nom_entreprise: str = Field(
        description="Nom de l'entreprise dans laquelle l'expérience professionnelle a eu lieu."
    )
    duree_experience: str = Field(
        description="Durée de la mission ou de l'expérience professionnelle en nombre d'années et de mois. Si en nombre d'années ajouter 'ans'. Si en nombre de mois ajouter 'mois'. Si en nombre de mois et années, séparer avec une virgule, exemple : 'X années, Y mois' Indiquez N/A si non indiquée."
    )
    date_debut_experience: datetime.date = Field(
        description="Date de début de la mission ou de l'expérience professionnelle dans l'entreprise au format python 'datetime.date'.  Indiquez N/A si non indiquée."
    )
    date_fin_experience: datetime.date = Field(
        description="Date de fin de la mission ou de l'expérience professionnelle dans l'entreprise au format python 'datetime.date'. Indiquez N/A si non indiquée."
    )
    nom_poste: str = Field(
        description="Nom ou intitulé du poste dans l'entreprise. Indiquez N/A si non indiquée."
    )
    stack_technique: List[StackTechnique] = Field(
        description="Liste des environnements techniques et des outils technologiques de la mission. Indiquez N/A si non indiquée."
    )


class EntrepriseExperienceTaches(BaseModel):
    nom_entreprise: str = Field(
        description="Nom de l'entreprise dans laquelle l'expérience professionnelle a eu lieu."
    )
    nom_poste: str = Field(description="Nom ou intitulé du poste dans l'entreprise.")
    role: List[TacheEntreprise] = Field(
        description="Enumérer et résumer les tâches, sous-tâches, réalisations et activités réalisés dans l'entreprise. Indiquez N/A si non indiquée."
    )


class TypeProfile(BaseModel):
    type: str = Field(
        description="Code ou libellé du profil recherché pour la mission, incluant les profils recherché en priorité et les profils alternatifs acceptés."
    )


class ElementOffreTechnique(BaseModel):
    element: str = Field(description="Elément de l'offre technique.")


class SousCritereTechnique(BaseModel):
    critere: str = Field(description="Sous-critère technique d'évaluation.")
    ponderation: int = Field(description="Pondération du sous-critère technique.")


class Tache(BaseModel):
    tache_et_responsabilite: str = Field(
        description="Tâche attendue et responsabilité(s) associée(s)."
    )


class Competence(BaseModel):
    competence: str = Field(
        description="Compétence ou aptitude attendue pour réalisation de la mission."
    )


class ConditioRegulariteOffre(BaseModel):
    competence: str = Field(description="Condition de régularité de l'offre.")


class Diplome(BaseModel):
    niveau_etude: str = Field(
        description="Niveau d'étude atteint à la fin de la formation. Exemple : 'Bac+2' pour un diplôme de technicien, 'Bac+3' pour un diplôme de licence, 'Bac+5' pour un diplôme de master ou un diplôme d'école d'ingénieur et de commerce, 'Bac+8' pour un doctorat ou une thèse. Indiquer '-1' si non indiqué."
    )
    date_obtention: datetime.date = Field(
        description="Année d'obtention du diplôme. Indiquer au format 'datetime.MAXYEAR' si non indiquée."
    )
    diplome: str = Field(
        description="Nom ou intitulé du diplôme d'études supérieures obtenu."
    )
    competences_acquises: List[CompetenceAcquiseDiplome] = Field(
        description="Liste des compétences acquises au cours de la formation diplomante, si mentionnée."
    )


class Certification(BaseModel):
    date_obtention: str = Field(
        description="Année d'obtention de la certification. Indiquez N/A si non indiquée."
    )
    certification: str = Field(description="Nom ou intitulé de la certification.")
    competences_acquises: List[CompetenceAcquiseCertification] = Field(
        description="Liste des compétences acquises au cours de la certification, si mentionnée."
    )


class Langue(BaseModel):
    langue: str = Field(description="Nom de la langue pratiquée.")
    niveau: str = Field(
        description="Niveau de maitrise de la langue. Indiquez N/A si non indiquée."
    )


class CDCRECJsonOutputFormat(BaseModel):
    numero_dossier_consultation: str = Field(
        description="Numéro du dossier de consultation. Ce numéro de dossier est constitué de 14 caractères avec le format suivant: l'année sur les 4 premiers caractères, le trigramme 'DOS' et 7 chiffres.  Exemple: 2023DOS0550696"
    )
    objectif_de_la_mission: str = Field(
        description="Objectifs principaux de la mission."
    )
    synthese: str = Field(
        description="Synthèse de la description du besoin exprimé en 2 phrases maximum."
    )
    duree_tranche_ferme: int = Field(
        description="Durée ou volume (en jours) de la tranche ferme de la prestation."
    )
    date_debut_tranche_ferme: datetime.date = Field(
        description="Date de début de la mission (tranche ferme) au format python 'datetime.date'."
    )
    date_fin_tranche_ferme: datetime.date = Field(
        description="Date de fin de la mission (tranche fin)  au format python 'datetime.date'."
    )
    duree_tranche_optionelle: int = Field(
        description="Durée ou volume (en jours) de la tranche optionnelle de la prestation."
    )
    duree_de_la_mission: int = Field(description="Durée de la mission (en jours).")
    duree_de_la_mission_avec_option: int = Field(
        description="Durée totale de la mission (en jours)  dans le cas de levée d'option, c’est-à-dire durée de la mission incluant la tranche ferme et la ou les tranche(s) optionnelle(s)."
    )
    nombre_de_profils: int = Field(
        description="Nombre de personne(s) ou profil(s) recherché pour la réalisation de la mission."
    )
    types_de_profils: List[TypeProfile] = Field(
        description="Liste des codes ou libellés des profils acceptés pour réaliser la mission, incluant les profils préférés ou recherché en priorité et les possibilités de variante."
    )
    taches_et_responsabilites: List[Tache] = Field(
        description="Liste des tâches et responsabilités qui constituent la mission. N'indiquer que les éléments présents dans le document."
    )
    competences_du_profils: List[Competence] = Field(
        description="Liste des compétences et aptitudes recherchées pour la mission. N'indiquer que les éléments présents dans le document."
    )
    stack_technique: List[StackTechnique] = Field(
        description="Liste des environnements techniques et des outils technologiques de la mission. Indiquez N/A si non indiquée."
    )
    nombre_de_profils: int = Field(
        description="Nombre de personne(s) recherchée(s) pour la mission."
    )
    types_de_profils: List[TypeProfile] = Field(
        description="Types de profils recherchés pour la missison."
    )
    offre_technique: List[ElementOffreTechnique] = Field(
        description="Liste des éléments et des pièces attendus dans la réponse ou offre technique."
    )
    condition_regularite_offre: List[ConditioRegulariteOffre] = Field(
        description="Liste des conditions de régularité de l'offre."
    )
    ponderation_critère_financier: int = Field(
        description="Pondération de la notation financière, c’est-à-dire liée aux critères financiers."
    )
    ponderation_critère_technique: int = Field(
        description="Pondération de la notation technique, c’est-à-dire liée aux critères et sous-critères techniques."
    )
    sous_criteres_techniques_et_ponderation: List[SousCritereTechnique] = Field(
        description="Liste des sous-critères techniques d'évaluation ainsi que leur pondération respective."
    )
    note_eliminatoire: int = Field(
        description="Note technique éliminatoire sur 20. Indiquer N/A si les détails ne sont pas indiqués."
    )


class CVExperiencesJsonOutputFormat(BaseModel):
    experiences_entreprise: List[EntrepriseExperience] = Field(
        description="Liste des expériences professionnelles du profil proposé. Indiquer aussi les détails des expériences quand ceux-ci sont disponibles. Indiquer N/A si les détails ne sont pas indiqués."
    )


class CVExperiencesTachesJsonOutputFormat(BaseModel):
    experiences_entreprise: List[EntrepriseExperienceTaches] = Field(
        description="Liste des expériences professionnelles du profil proposé. Indiquer aussi les détails des expériences quand ceux-ci sont disponibles. Indiquer N/A si les détails ne sont pas indiqués."
    )


class CVDiplomesJsonOutputFormat(BaseModel):
    diplomes: List[Diplome] = Field(
        description="Indiquer la liste des diplômes obtenus par le profil proposé. Indiquer uniquement les diplômes. Ne pas indiquer d'expériences."
    )
    certifications: List[Certification] = Field(
        description="Liste des certifications obtenues par le profil proposé. Indiquer uniquement les certifications. Ne pas indiquer d'expériences"
    )
    langues_parlees: List[Langue] = Field(
        description="Indiquer les langues parlées par le profil proposé. N'indiquer que les langues mentionnées dans le document."
    )


class ActivitesEtTaches(BaseModel):
    type: str = Field(
        description="Une activitée, une tâche, une réalisation ou une responsabilité sur poste."
    )


class NiveauSeniorite(BaseModel):
    type: str = Field(description="Nom du niveau de séniorité.")
    annee_exp_minimum: int = Field(
        description="Nombre d'années minimum d'expérience pertinente et correspondant à ce poste à ce niveau de séniorité"
    )
    annee_exp_maximum: Union[int, None] = Field(
        description="Nombre d'années maximum d'expérience pertinente et correspondant à ce poste à ce niveau de séniorité. Indiquer None si pas de date maximum."
    )


class Competences(BaseModel):
    type: str = Field(
        description="Type de profil accepté et aussi ouvert à variante s'il y a. Respectez la nomenclateure des profils. exemple: 104.S.PAR, 403.J.PROV, 901.S.PAR etc."
    )


class ReferentielJsonOutputFormat(BaseModel):
    nom_du_poste: str = Field(description="Nom du poste")
    code_du_poste: str = Field(description="Code du poste associé au nom du poste")
    description_des_missions: str = Field(
        description="Description des missions réalisées par une personne ayant cet intitulé de poste."
    )
    taches_et_responsabilites: List[ActivitesEtTaches] = Field(
        description="Liste des activitées, des tâches et responsabilités du poste. N'indiquez que les élements présents dans le document."
    )
    competences: List[Competences] = Field(
        description="Liste des compétences possédant une personne sur ce poste. Indiquez 'N/A' si non indiqués. N'indiquez que les élements présents dans le document."
    )
    niveau_seniorite: List[NiveauSeniorite] = Field(
        description="Liste niveaux de séniorité sur ce poste avec les années d'expériences requises. N'indiquez que les élements présents dans le document."
    )
