from openai import OpenAI
import re

# Constants
OPENAI_MODEL = "gpt-4o-mini"
MAX_CHUNK_SIZE = 2000  # Max chunk size for OpenAI API

class OpenAIProcessor:
    def __init__(self, model=OPENAI_MODEL):
        self.client = OpenAI()
        self.model = model

    def chunk_text(self, text, max_chunk_size=MAX_CHUNK_SIZE):
        """Chunk text into smaller parts for processing."""
        paragraphs = re.split(r"\n\s*\n", text)
        chunks, current_chunk, current_len = [], [], 0
        for para in paragraphs:
            if len(para) + current_len < max_chunk_size:
                current_chunk.append(para)
                current_len += len(para)
            else:
                chunks.append("\n".join(current_chunk))
                current_chunk, current_len = [para], len(para)
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return chunks

    def analyze_text_chunk(self, chunk):
        """Process a text chunk with OpenAI to extract regulatory information."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert legal analyst specializing in regulatory ontology modeling using the Unified Foundational Ontology (UFO) framework. "
                    "Given a chunk of regulatory text, extract, classify, and structure the information into the following ontology, ensuring relationships between endurants (entities), perdurants (processes/events), and social objects (commitments, rights, penalties) are explicitly captured. "
                    ""
                    "Endurants (Entities that Persist Over Time) "
                    "Regulated Entity: Entities required to comply with the regulation (e.g., property owners, eligible rental buildings, redevelopment companies). "
                    "Regulating Authority: The body responsible for defining and governing the regulation (e.g., a government agency, legislative council). "
                    "Enforcing Entity: The organization or agency responsible for ensuring compliance (e.g., an inspection or enforcement division). "
                    "Stakeholder: Other entities affected by the regulation (e.g., tenants, contractors, lenders). "
                    ""
                    "Entity Relationships "
                    "hasRegulatingAuthority(Regulation → RegulatingAuthority): Identifies the regulatory body governing the rule. "
                    "hasRegulatedEntity(Regulation → RegulatedEntity): Specifies which entities must comply. "
                    "hasEnforcingEntity(Regulation → EnforcingEntity): Defines the entity responsible for compliance enforcement. "
                    "hasStakeholder(Regulation → Stakeholder): Identifies entities indirectly impacted by the regulation. "
                    ""
                    "Perdurants (Processes and Events) "
                    "Regulation Enactment: The event/process in which the regulation becomes law or is amended. "
                    "Compliance Process: The required actions to fulfill regulatory obligations (e.g., filing applications, certification, documentation). "
                    "Violation Event: The triggering event that leads to penalties or sanctions (e.g., failure to substantiate costs, missing deadlines). "
                    "Non-Compliance Consequence: The sequence of actions taken when an entity fails to comply (e.g., revocation of tax benefits, fines). "
                    ""
                    "Event Relationships "
                    "triggersComplianceProcess(Regulation → ComplianceProcess): Specifies required compliance steps due to a regulation. "
                    "triggersViolationEvent(Regulation → ViolationEvent): Defines non-compliance triggers (e.g., missing documentation, failed audits). "
                    "resultsInConsequence(ViolationEvent → NonComplianceConsequence): Identifies penalties or outcomes for violations. "
                    ""
                    "Social Objects (Commitments, Norms, and Rights) "
                    "Regulation: The main regulation described in the text (e.g., tax abatement law, zoning rule). "
                    "Defined Conditions: The requirements or thresholds that must be met for eligibility (e.g., financial conditions, property usage). "
                    "Commitment & Obligation: The legally binding commitments imposed by the regulation (e.g., duty to notify tenants, record-keeping). "
                    "Rights & Benefits: The entitlements granted to entities under the regulation (e.g., tax relief, subsidies). "
                    "Penalties & Sanctions: The legal or financial consequences imposed for non-compliance (e.g., revocation of benefits, fines). "
                    "Reference Materials: Other legal texts or regulations that cite, reference, or expand upon this regulation. "
                    ""
                    "Social Object Relationships "
                    "definesCondition(Regulation → Condition): Specifies eligibility requirements for compliance. "
                    "imposesPenalty(Regulation → Penalty): Defines penalties imposed for non-compliance. "
                    "grantsRight(Regulation → Right): Specifies benefits awarded to compliant entities. "
                    "hasCommitment(Regulation → Commitment): Describes mandatory obligations for regulated entities. "
                    "references(Regulation → Reference): Links external laws, statutes, or related documents. "
                    ""
                    "Output Format "
                    "Return the results in JSON format, categorizing each extracted element under its appropriate UFO type (endurant, perdurant, or social object). "
                    "Additionally, return all explicit relationships (e.g., 'hasRegulatedEntity': { 'Regulation': 'J-51 Program', 'RegulatedEntity': 'Property Owners' }). "
                    "If multiple instances exist under a category, return them as an array of objects."
                )

            },
            {
                "role": "user",
                "content": f"Here is the policy text:\n\n{chunk}"
            }
        ]

        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages)
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: {str(e)}"