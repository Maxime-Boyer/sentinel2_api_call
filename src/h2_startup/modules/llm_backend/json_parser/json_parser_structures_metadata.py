import datetime
from typing import List, Union, Tuple

from langchain_core.pydantic_v1 import BaseModel, Field


class TacheEntrepriseMetadata(BaseModel):
    tache: Tuple[str, int] = Field(
        description="First value : Tâche ou réalisation ou activité réalisée dans l'entreprise. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class StackTechniqueMetadata(BaseModel):
    tache: Tuple[str, int] = Field(
        description="First value : Elément de l'environnement technique de la mission. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class CompetenceAcquiseDiplomeMetadata(BaseModel):
    tache: Tuple[str, int] = Field(
        description="First value : Compétence acquise au cours de la formation diplomante. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class CompetenceAcquiseCertificationMetadata(BaseModel):
    tache: Tuple[str, int] = Field(
        description="First value : Compétence acquise au cours de la certification. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class EntrepriseExperienceMetadata(BaseModel):
    nom_entreprise: Tuple[str, int] = Field(
        description="First value : Nom de l'entreprise dans laquelle l'expérience professionnelle a eu lieu. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    duree_experience: Tuple[str, int] = Field(
        description="First value : Durée de la mission ou de l'expérience professionnelle en nombre d'années et de mois. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    date_debut_experience: Tuple[datetime.date, int] = Field(
        description="First value : Date de début de la mission ou de l'expérience professionnelle dans l'entreprise. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    date_fin_experience: Tuple[datetime.date, int] = Field(
        description="First value : Date de fin de la mission ou de l'expérience professionnelle dans l'entreprise. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    nom_poste: Tuple[str, int] = Field(
        description="First value : Nom ou intitulé du poste dans l'entreprise. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    stack_technique: List[StackTechniqueMetadata] = Field(
        description="Liste des environnements techniques et des outils technologiques de la mission."
    )


class EntrepriseExperienceTachesMetadata(BaseModel):
    nom_entreprise: Tuple[str, int] = Field(
        description="First value : Nom de l'entreprise dans laquelle l'expérience professionnelle a eu lieu. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    nom_poste: Tuple[str, int] = Field(
        description="First value : Nom ou intitulé du poste dans l'entreprise. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    role: List[TacheEntrepriseMetadata] = Field(
        description="Tâches, sous-tâches, réalisations et activités réalisés dans l'entreprise."
    )


class TypeProfileMetadata(BaseModel):
    type: Tuple[str, int] = Field(
        description="First value : Code ou libellé du profil recherché pour la mission. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class ElementOffreTechniqueMetadata(BaseModel):
    element: Tuple[str, int] = Field(
        description="First value : Elément de l'offre technique. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class SousCritereTechniqueMetadata(BaseModel):
    critere: Tuple[str, int] = Field(
        description="First value : Sous-critère technique d'évaluation. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    ponderation: Tuple[int, int] = Field(
        description="First value : Pondération du sous-critère technique. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class TacheMetadata(BaseModel):
    tache_et_responsabilite: Tuple[str, int] = Field(
        description="First value : Tâche attendue et responsabilité(s) associée(s). Second value : le numéro de la page où l'information de la first value de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class CompetenceMetadata(BaseModel):
    competence: Tuple[str, int] = Field(
        description="First value : Compétence ou aptitude attendue pour réalisation de la mission. Second value : le numéro de la page où l'information de la first value de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class ConditioRegulariteOffreMetadata(BaseModel):
    competence: Tuple[str, int] = Field(
        description="First value : Condition de régularité de l'offre. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class DiplomeMetadata(BaseModel):
    niveau_etude: Tuple[str, int] = Field(
        description="First value : Niveau d'étude atteint à la fin de la formation. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    date_obtention: Tuple[datetime.date, int] = Field(
        description="First value : Année d'obtention du diplôme. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    diplome: Tuple[str, int] = Field(
        description="First value : Nom ou intitulé du diplôme d'études supérieures obtenu. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    competences_acquises: List[CompetenceAcquiseDiplomeMetadata] = Field(
        description="Liste des compétences acquises au cours de la formation diplomante, si mentionnées."
    )


class CertificationMetadata(BaseModel):
    date_obtention: Tuple[str, int] = Field(
        description="First value : Année d'obtention de la certification. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    certification: Tuple[str, int] = Field(
        description="First value : Nom ou intitulé de la certification. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    competences_acquises: List[CompetenceAcquiseCertificationMetadata] = Field(
        description="Liste des compétences acquises au cours de la certification, si mentionnées."
    )


class LangueMetadata(BaseModel):
    langue: Tuple[str, int] = Field(
        description="First value : Nom de la langue pratiquée. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    niveau: Tuple[str, int] = Field(
        description="First value : Niveau de maitrise de la langue. Second value : le numéro de la page où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class CDCRECJsonOutputFormatMetadata(BaseModel):
    numero_dossier_consultation: Tuple[str, int] = Field(
        description="First value : Numéro du dossier de consultation. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    objectif_de_la_mission: Tuple[str, int] = Field(
        description="First value : Objectifs principaux de la mission. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    synthese: Tuple[str, int] = Field(
        description="First value : Synthèse de la description du besoin exprimé. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    duree_tranche_ferme: Tuple[int, int] = Field(
        description="First value : Durée ou volume (en jours) de la tranche ferme de la prestation. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    date_debut_tranche_ferme: Tuple[datetime.date, int] = Field(
        description="First value : Date de début de la mission (tranche ferme). Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    date_fin_tranche_ferme: Tuple[datetime.date, int] = Field(
        description="First value : Date de fin de la mission (tranche fin). Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    duree_tranche_optionelle: Tuple[int, int] = Field(
        description="First value : Durée ou volume (en jours) de la tranche optionnelle de la prestation. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    duree_de_la_mission: Tuple[int, int] = Field(
        description="First value : Durée de la mission (en jours). Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    duree_de_la_mission_avec_option: Tuple[int, int] = Field(
        description="First value : Durée totale de la mission (en jours)  dans le cas de levée d'option. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    nombre_de_profils: Tuple[int, int] = Field(
        description="First value : Nombre de personne(s) ou profil(s) recherché pour la réalisation de la mission. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    types_de_profils: List[TypeProfileMetadata] = Field(
        description="Liste des codes ou libellés des profils acceptés pour réaliser la mission, incluant les profils préférés ou recherché en priorité et les possibilités de variante."
    )
    taches_et_responsabilites: List[TacheMetadata] = Field(
        description="Liste des tâches et responsabilités qui constituent la mission."
    )
    competences_du_profils: List[CompetenceMetadata] = Field(
        description="Liste des compétences et aptitudes recherchées pour la mission."
    )
    stack_technique: List[StackTechniqueMetadata] = Field(
        description="Liste des environnements techniques et des outils technologiques de la mission."
    )
    offre_technique: List[ElementOffreTechniqueMetadata] = Field(
        description="Liste des éléments et des pièces attendus dans la réponse ou offre technique."
    )
    condition_regularite_offre: List[ConditioRegulariteOffreMetadata] = Field(
        description="Liste des conditions de régularité de l'offre."
    )
    ponderation_critère_financier: Tuple[int, int] = Field(
        description="First value : Pondération de la notation financière. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    ponderation_critère_technique: Tuple[int, int] = Field(
        description="First value : Pondération de la notation technique. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )
    sous_criteres_techniques_et_ponderation: List[SousCritereTechniqueMetadata] = Field(
        description="Liste des sous-critères techniques d'évaluation ainsi que leur pondération respective."
    )
    note_eliminatoire: Tuple[int, int] = Field(
        description="First value : Note technique éliminatoire de 0 à 20 sur 20. Second value : le numéro de la page au sein du document où l'information de la first value a été trouvée. Si information de la first value non indiquée, indiquer -1 pour la second value."
    )


class CVExperiencesJsonOutputFormatMetadata(BaseModel):
    experiences_entreprise: List[EntrepriseExperienceMetadata] = Field(
        description="Liste des expériences professionnelles du profil proposé."
    )


class CVExperiencesTachesJsonOutputFormatMetadata(BaseModel):
    experiences_entreprise: List[EntrepriseExperienceTachesMetadata] = Field(
        description="Liste des expériences professionnelles du profil proposé."
    )


class CVDiplomesJsonOutputFormatMetadata(BaseModel):
    diplomes: List[DiplomeMetadata] = Field(
        description="Indiquer la liste des diplômes obtenus par le profil proposé."
    )
    certifications: List[CertificationMetadata] = Field(
        description="Liste des certifications obtenues par le profil proposé."
    )
    langues_parlees: List[LangueMetadata] = Field(
        description="Indiquer les langues parlées par le profil proposé."
    )
