def metaprompt_single_resume(REQUIREMENTS, CRITERIA, RESUME, SCALE):
    return (
        f"""
    Vous êtes un assistant d'analyse des compétences techniques de CV dans le cadre de réponse à appel
    d'offre du groupe SNCF. En vous basant sur un critère d'évaluation qui vous est fourni, votre tâche 
    est d'évaluer un CV uniquement par rapport à ce critère.

    Voici les informations dont vous disposez :

    <Requirements>
    {REQUIREMENTS}
    </Requirements>

    <Criteria>
    {CRITERIA}
    </Criteria>

    <Resume>
    {RESUME}
    </Resume>

    <Scale>
    {SCALE}
    </Scale>
    """
        + """
    Commencez par lire attentivement les exigences attendues pour la mission et le critère d'évaluation. Ensuite, analysez le CV par rapport
    au critère fourni. Fournissez d'abord une justification détaillée de la note que
    vous attribuez au candidat par rapport au critère d'évaluation. Utilisez les informations du CV pour justifier la note attribuée. 
    Vous devez expliquer les points forts et les points faibles du CV au regard du critère fourni.

    Après avoir fourni la justification, donnez une note numérique entre 1 et 5 en vous basant sur
    l'échelle de notation fournie.

    Ensuite, produisez un JSON avec la note attribuée et la
    justification associée.

    Le format du JSON doit être le suivant :

    {
    'critère': {
    'justification': 'Justification détaillée pour la note',
    'score': X
    }
    }

    Remplacez "critère" par la chaîne de caractères réelles du critère. Assurez-vous que la
    justification soit claire et détaillée, et que le score soit conforme à l'échelle de notation
    fournie.

    <scratchpad>
    Vous pouvez utiliser cette zone pour prendre des notes et organiser vos pensées avant de produire le
    JSON final.
    </scratchpad>

    <json_output>
    Écrivez votre sortie JSON ici.
    </json_output>
    """
    )


def metaprompt_multi_resume(
    REQUIREMENTS, CRITERIA, LIST_RESUME, LIST_MARKED_JSONS, SCALE
):
    return (
        f"""1. Présenter la tâche et les entrées
    2. Demander à l'assistant d'analyser les exigences et les critères
    3. Demander à l'assistant d'analyser les CV et les notes existantes
    4. Demander à l'assistant d'adapter les notes en comparant les CV entre eux et par rapport aux
    exigences
    5. Demander à l'assistant de produire les JSONs finaux avec les notes adaptées
    </Instructions Structure>

    <Instructions>
    Votre tâche est d'analyser les compétences techniques de CV dans le cadre de réponses à des appels
    d'offres du groupe SNCF. Vous recevrez les entrées suivantes :

    - REQUIREMENTS : Le contenu des exigences de l'appel d'offres
    - CRITERIA : Les critères techniques pondérés pour l'évaluation
    - LIST_RESUME : La liste des CV des répondants
    - LIST_MARKED_JSONS : La liste des notes techniques préalablement construites pour chaque CV, au
    format JSON avec une note entre 1 et 5 pour chaque critère
    - SCALE : L'échelle d'évaluation pour savoir comment attribuer les notes

    <requirements>
    {REQUIREMENTS}
    </requirements>

    <criterias>
    {CRITERIA}
    </criterias>

    <list_resumes>
    {LIST_RESUME}
    </list_resumes>

    <list_marked_jsons>
    {LIST_MARKED_JSONS}
    </list_marked_jsons>

    <scale>
    {SCALE}
    </scale>

    Commencez par analyser attentivement <requirements>{REQUIREMENTS}</requirements> et
    <criterias>{CRITERIA}</criterias> pour bien comprendre les exigences de l'appel d'offres et les
    critères d'évaluation.

    <scratchpad>
    Analysez les exigences et les critères ici.
    </scratchpad>

    Ensuite, analysez <list_resumes>LIST_RESUME</list_resumes> et
    <list_marked_jsons>LIST_MARKED_JSONS</list_marked_jsons> pour comprendre les compétences des
    différents répondants et les notes qui leur ont été attribuées.

    <scratchpad>
    Analysez les CV et les notes existantes ici.
    </scratchpad>

    Maintenant, en vous basant sur votre analyse des exigences, des critères et des CV, vous devez
    adapter les notes existantes. Comparez les CV entre eux et par rapport aux exigences du client.
    Utilisez <scale>{SCALE}</scale> pour savoir comment attribuer les notes.

    Pour chaque CV et chaque critère, donnez d'abord une justification de la note que vous attribuez, puis la note
    elle-même entre 0 et 5.

    ...

    Une fois que vous avez bien analysé les jsons des notes par critères ainsi que les CV entre eux en les comparant. Produisez un json nouveau json pour chaque CV en entrée, en suivant le format :
    """
        + """

    {
    'critère1': {
    'justification': 'Justification détaillée pour la note',
    'score': X
    }
    'critère2': {
    'justification': 'Justification détaillée pour la note',
    'score': Y
    }
    }
    
    Remplacez "critère" par la chaîne de caractères réelles du critère. Assurez-vous que la
    justification soit claire et détaillée, et que le score soit conforme à l'échelle de notation
    fournie.

    Vérifier que les jsons sont valides et utilisables par la fonction json.loads en python. Chaque json retourné est entouré de balises json_output. 
    
    Il doit y avoir exactement le même nombre de json en sortie (json_output) que de nombre de json et CV en entrée. 
    
    <json_output>
    Ecrivez chaque JSON final entre ces deux tags.
    </json_output>

    </Instructions>"""
    )
