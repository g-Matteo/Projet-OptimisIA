from pydantic import BaseModel, Field
from typing import Literal

def build_JSON_SCHEMA(english:bool):
    if english:
        ton = Literal["Positive", "Negative", "Neutral", "Not mentioned"]

        class PatientFeedback(BaseModel):
            care_pathway_smoothness_and_personalization: ton = Field(
                ..., alias="The smoothness and personalization of the care pathway"
            )
            reception_and_admission: ton = Field(
                ..., alias="Reception and admission"
            )
            administrative_procedures: ton = Field(
                ..., alias="Administrative procedures"
            )
            speed_of_care_and_waiting_time: ton = Field(
                ..., alias="Speed of care and waiting time"
            )
            access_to_operating_room: ton = Field(
                ..., alias="Access to the operating room"
            )
            discharge_from_facility: ton = Field(
                ..., alias="Discharge from the facility"
            )
            follow_up_after_hospital_stay: ton = Field(
                ..., alias="Follow-up after hospital stay"
            )
            additional_charges_and_fees: ton = Field(
                ..., alias="Additional charges and excess fees"
            )
            information_and_explanations: ton = Field(
                ..., alias="Information and explanations"
            )
            humanity_and_availability_of_professionals: ton = Field(
                ..., alias="Humanity and availability of professionals"
            )
            medical_and_paramedical_care: ton = Field(
                ..., alias="Medical and paramedical care"
            )
            patient_rights: ton = Field(
                ..., alias="Patient rights"
            )
            pain_management_and_medications: ton = Field(
                ..., alias="Pain management and medications"
            )
            maternity_and_pediatrics: ton = Field(
                ..., alias="Maternity and pediatrics"
            )
            access_to_facility: ton = Field(
                ..., alias="Access to the facility"
            )
            premises_and_rooms: ton = Field(
                ..., alias="Premises and rooms"
            )
            privacy: ton = Field(
                ..., alias="Privacy"
            )
            noise_level: ton = Field(
                ..., alias="Noise level"
            )
            room_temperature: ton = Field(
                ..., alias="Room temperature"
            )
            meals_and_snacks: ton = Field(
                ..., alias="Meals and snacks"
            )
            wifi_and_tv_services: ton = Field(
                ..., alias="WiFi and TV services"
            )
        return PatientFeedback


    else:
        ton =Literal["Positif", "Négatif", "Neutre", "Pas mentionné"]

        class PatientFeedback(BaseModel):
            la_fluidite_et_la_personnalisation_du_parcours: ton = Field(
                ..., alias="La fluidité et la personnalisation du parcours"
            )
            l_accueil_et_l_admission: ton = Field(
                ..., alias="L’accueil et l’admission"
            )
            le_circuit_administratif: ton = Field(
                ..., alias="Le circuit administratif"
            )
            la_rapidite_de_prise_en_charge_et_le_temps_d_attente: ton = Field(
                ..., alias="La rapidité de prise en charge et le temps d’attente"
            )
            l_acces_au_bloc: ton = Field(
                ..., alias="L’accès au bloc"
            )
            la_sortie_de_l_etablissement: ton = Field(
                ..., alias="La sortie de l’établissement"
            )
            le_suivi_du_patient_apres_le_sejour_hospitalier: ton = Field(
                ..., alias="Le suivi du patient après le séjour hospitalier"
            )
            les_frais_supplementaires_et_depassements_d_honoraires: ton = Field(
                ..., alias="Les frais supplémentaires et dépassements d’honoraires"
            )
            l_information_et_les_explications: ton = Field(
                ..., alias="L’information et les explications"
            )
            l_humanite_et_la_disponibilite_des_professionnels: ton = Field(
                ..., alias="L’humanité et la disponibilité des professionnels"
            )
            les_prises_en_charges_medicales_et_paramedicales: ton = Field(
                ..., alias="Les prises en charges médicales et paramédicales"
            )
            droits_des_patients: ton = Field(
                ..., alias="Droits des patients"
            )
            gestion_de_la_douleur_et_medicaments: ton = Field(
                ..., alias="Gestion de la douleur et médicaments"
            )
            maternite_et_pediatrie: ton = Field(
                ..., alias="Maternité et pédiatrie"
            )
            l_acces_a_l_etablissement: ton = Field(
                ..., alias="L’accès à l’établissement"
            )
            les_locaux_et_les_chambres: ton = Field(
                ..., alias="Les locaux et les chambres"
            )
            l_intimite: ton = Field(
                ..., alias="L’intimité"
            )
            le_calme_volume_sonore: ton = Field(
                ..., alias="Le calme/volume sonore"
            )
            la_temperature_de_la_chambre: ton = Field(
                ..., alias="La température de la chambre"
            )
            les_repas_et_collations: ton = Field(
                ..., alias="Les repas et collations"
            )
            les_services_wifi_et_tv: ton = Field(
                ..., alias="Les services WiFi et TV"
            )
        return PatientFeedback