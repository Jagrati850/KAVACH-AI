"""
KAVACH AI — Retrieval-Augmented Generation (RAG) Engine
RAG system for answering citizen queries utilizing authoritative Indian government advisories.
Source documents compiled from: MHA, CERT-In, NCRP, and RBI.
"""

import re
import math
from typing import Any, Dict, List, Set


# Curated corpus of official cyber threat advisories
GOVERNMENT_COUPLES = [
    # MHA / NCRP Advisories
    {
        "id": "mha_001",
        "source": "Ministry of Home Affairs (MHA) / National Cyber Crime Reporting Portal (NCRP)",
        "document_type": "Advisory",
        "title": "Explosion in Digital Arrest Scam Networks",
        "content": (
            "Cyber criminals impersonating law enforcement officers from the Central Bureau of "
            "Investigation (CBI), state police, Customs department, Enforcement Directorate (ED), "
            "or Narcotics Control Bureau (NCB) are contacting citizens via audio/video calls. "
            "Victims are falsely told that a courier parcel containing illegal narcotics (like MDMA or drugs) "
            "or passport materials was intercepted in their name, or that their bank accounts are "
            "implicated in international money laundering rings. Fraudsters then enforce 'Digital Arrest' "
            "or 'Digital Custody' by instructing victims to remain connected on Skype, WhatsApp, or Zoom "
            "video continuously under threatened arrest. MHA clarifies: No government agency, department, "
            "or law enforcement officer executes digital arrests or demands money, safety funds, or security "
            "deposits over video/phone call. Disconnect immediately and call 1930."
        ),
        "tags": {"digital arrest", "skype", "cbi", "police", "customs", "drugs", "mdma", "parcel", "custody", "narcotics"},
        "url": "https://cybercrime.gov.in/Webform/Advisory.aspx"
    },
    {
        "id": "mha_002",
        "source": "National Cyber Crime Reporting Portal (NCRP)",
        "document_type": "Guidelines",
        "title": "Reporting Cyber Frauds & Golden Hour Protocol",
        "content": (
            "In financial cyber fraud situations, reporting the request within the 'Golden Hour' (the first "
            "2 hours of occurrence) is highly critical. Calling the citizen helpline 1930 immediately enables "
            "banks and the law enforcement network to trigger transaction-halting mechanisms, freezing the "
            "stolen funds on the recipient's bank accounts, e-wallets, or UPI handles. Victims can also file a "
            "detailed complaint online at the National Cyber Crime Portal (cybercrime.gov.in) attaching transaction "
            "receipts, UPI reference IDs, screenshot evidence, and phone log records of callers."
        ),
        "tags": {"1930", "report", "golden hour", "portal", "freeze", "financial fraud", "evidence", "complaint"},
        "url": "https://cybercrime.gov.in"
    },
    # RBI Advisories
    {
        "id": "rbi_001",
        "source": "Reserve Bank of India (RBI)",
        "document_type": "Fraud Advisory",
        "title": "UPI Safety, PIN Protocols, and Phishing Safeguards",
        "content": (
            "Under the RBI's 'RBI Kehta Hai' campaign, residents are reminded that a UPI PIN is required ONLY "
            "when sending money or making payments, never for receiving money or claiming cashback/scratch cards. "
            "Any website, SMS link, or caller requesting your UPI PIN to facilitate an incoming transaction or "
            "cancel a pending fine is malicious. Never enter your UPI PIN on screens prompted by strangers. RBI "
            "also stresses never sharing your 4/6-digit UPI PIN, Credit/Debit card CVV, bank passwords, or one-time "
            "passcodes (OTPs) with anyone, including individuals claiming to be bank employees or officers."
        ),
        "tags": {"rbi", "upi pin", "cashback", "otp", "cvv", "card", "bank account", "receive money"},
        "url": "https://rbi.org.in"
    },
    {
        "id": "rbi_002",
        "source": "Reserve Bank of India (RBI)",
        "document_type": "Directive",
        "title": "Customer Liability Limits in Unauthorized Transactions",
        "content": (
            "RBI directives state that a customer's liability is zero in cases of unauthorized electronic banking "
            "transactions if they notify the bank within three working days of the transaction's occurrence, and "
            "the fraud is due to bank negligence or third-party breaches where the customer has no fault. If the "
            "reporting delay is between four to seven working days, the liability is capped (ranging from ₹5,000 to "
            "₹25,000 depending on account category). Reporting delayed beyond seven working days is subject to "
            "individual bank policies. Prompt reporting to both the bank and the law enforcement framework is essential."
        ),
        "tags": {"rbi", "liability", "zero liability", "bank notification", "unauthorized transaction", "reporting delay"},
        "url": "https://rbi.org.in"
    },
    # CERT-In Advisories
    {
        "id": "cert_001",
        "source": "Indian Computer Emergency Response Team (CERT-In)",
        "document_type": "Security Advisory",
        "title": "Malicious Android Trojan Apps (Masergy, Sofa, Chameleon)",
        "content": (
            "CERT-In has observed active distribution of info-stealing Android Trojans disguised as utility tools, "
            "system updates, online banking assistants, or WhatsApp updates. Once sideloaded via third-party web links "
            "or text messages (SMS), these trojans illicitly hijack Accessibility Services permissions. This grants "
            "attackers capability to record keystrokes, capture OTPs from dual-factor notifications, capture "
            "personal contacts, and perform overlays on top of official mobile banking apps to steal credentials. "
            "CERT-In advises: Disable installs from unknown sources, avoid clicking SMS web links, check app "
            "permissions closely, and only use Google Play Store or Apple App Store."
        ),
        "tags": {"cert-in", "trojan", "android", "malware", "sideload", "otp", "permissions", "play store"},
        "url": "https://www.cert-in.org.in"
    },
    {
        "id": "cert_002",
        "source": "Indian Computer Emergency Response Team (CERT-In)",
        "document_type": "Advisory",
        "title": "Ransomware Campaigns and Defensive Strategies",
        "content": (
            "Active phishing campaigns are distributing ransomware variants Targeting individuals and enterprise infrastructure. "
            "These attacks encrypt critical documents, databases, and photos, rendering system files inaccessible, "
            "followed by ransom demands in cryptocurrency. CERT-In suggests maintaining offline backups of critical data, "
            "disabling Remote Desktop Protocol (RDP) exposures, updating software packages regularly, and refusing "
            "ransom demands. Paying ransoms does not guarantee decryption key receipt and funds subsequent "
            "cybercriminal organizations. Report infected nodes immediately for containment guidelines."
        ),
        "tags": {"cert-in", "ransomware", "phishing", "cryptocurrency", "backup", "rdp", "encryption"},
        "url": "https://www.cert-in.org.in"
    }
]


class RAGEngine:
    """
    Modular Retrieval-Augmented Generation (RAG) Engine.
    Leverages TF-IDF similarity vectors to extract valid context from government advisories,
    then generates an structured answer mimicking LLM summary frameworks.
    """

    def __init__(self):
        self.corpus = GOVERNMENT_COUPLES
        self.stopwords = {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
            "arent", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
            "but", "by", "cant", "cannot", "could", "did", "didnt", "do", "does", "doesnt", "doing", 
            "dont", "down", "during", "each", "few", "for", "from", "further", "had", "hadnt", "has", 
            "hasnt", "have", "havent", "having", "he", "hed", "hell", "hes", "her", "here", "heres", 
            "hers", "herself", "him", "himself", "his", "how", "hows", "i", "id", "ill", "im", "ive", 
            "if", "in", "into", "is", "isnt", "it", "its", "itself", "lets", "me", "more", "most", "mustnt", 
            "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", 
            "our", "ours", "ourselves", "out", "over", "own", "same", "shant", "she", "shed", "shell", 
            "shes", "should", "shouldnt", "so", "some", "such", "than", "that", "thats", "the", "their", 
            "theirs", "them", "themselves", "then", "there", "theres", "these", "they", "theyd", "theyll", 
            "theyre", "theyve", "this", "those", "through", "to", "too", "under", "until", "up", "very", 
            "was", "wasnt", "we", "wed", "well", "were", "weve", "werent", "what", "whats", "when", 
            "whens", "where", "wheres", "which", "while", "who", "whos", "whom", "why", "whys", "with", 
            "wont", "would", "wouldnt", "you", "youd", "youll", "youre", "youve", "your", "yours", 
            "yourself", "yourselves"
        }

    def _tokenize(self, text: str) -> List[str]:
        """Cleans and tokenizes text, removing common stopwords."""
        words = re.findall(r'\b[a-z]{2,}\b', text.lower())
        return [w for w in words if w not in self.stopwords]

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two frequency vector mappings."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0

        dot_product = sum(vec1[x] * vec2[x] for x in intersection)
        sum1 = sum(v ** 2 for v in vec1.values())
        sum2 = sum(v ** 2 for v in vec2.values())

        if sum1 == 0.0 or sum2 == 0.0:
            return 0.0

        return dot_product / (math.sqrt(sum1) * math.sqrt(sum2))

    def _get_tf_vector(self, tokens: List[str]) -> Dict[str, float]:
        """Get term frequency vector mapping."""
        vec = {}
        for t in tokens:
            vec[t] = vec.get(t, 0.0) + 1.0
        return vec

    def query(self, user_question: str) -> Dict[str, Any]:
        """
        Processes citizen query, retrieves top context documents, and synthesizes 
        authoritative advisory synthesis.
        """
        query_tokens = self._tokenize(user_question)
        if not query_tokens:
            return self._fallback_response(user_question)

        query_vec = self._get_tf_vector(query_tokens)

        # Match documents
        scored_docs = []
        for doc in self.corpus:
            # Gather all text elements in document (title + content + tag names)
            doc_text = doc["title"] + " " + doc["content"] + " " + " ".join(doc["tags"])
            doc_tokens = self._tokenize(doc_text)
            doc_vec = self._get_tf_vector(doc_tokens)

            # Boost score if tags are hit directly by query
            tag_overlaps = len(set(query_tokens) & doc["tags"])
            similarity = self._cosine_similarity(query_vec, doc_vec)
            
            final_score = similarity + (tag_overlaps * 0.15)
            if final_score > 0.05:
                scored_docs.append((final_score, doc))

        # Sort documents by similarity score
        scored_docs = sorted(scored_docs, key=lambda x: x[0], reverse=True)

        if not scored_docs:
            return self._fallback_response(user_question)

        # Take top matches (up to 2 for synthesis)
        top_matches = scored_docs[:2]
        retrieved_contexts = [item[1] for item in top_matches]

        answer = self._synthesize_response(user_question, retrieved_contexts)

        return {
            "query": user_question,
            "answer": answer["response"],
            "key_actions": answer["key_actions"],
            "retrieved_sources": [
                {
                    "title": doc["title"],
                    "source": doc["source"],
                    "document_type": doc["document_type"],
                    "relevance_score": round(score, 4),
                    "url": doc["url"]
                }
                for score, doc in top_matches
            ]
        }

    def _synthesize_response(self, query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize advice using extracted trusted contexts."""
        response_text = ""
        key_actions = []

        primary_doc = contexts[0]
        title = primary_doc["title"]
        source = primary_doc["source"]
        content = primary_doc["content"]

        # Parse contexts to extract standard recommendations
        if "digital arrest" in primary_doc["tags"] or any("digital" in t for t in primary_doc["tags"]):
            response_text = (
                f"Per official guidelines from the **{source}** regarding '{title}', "
                "please be advised that no government agency, court, or law enforcement division (CBI, Police, Customs, NCB, etc.) "
                "is legally authorized to execute 'digital custody' or 'digital arrest' over video applications such as Skype or Zoom. "
                "They will never demand deposits, online statement reviews, or personal password verifications."
            )
            key_actions = [
                "Disconnect Skype or WhatsApp video caller immediately",
                "Do NOT transfer payment, cash bonds, or safety deposits under pressure",
                "Report incident details to Cyber Crime helpline by calling 1930",
                "File official logs on the national portal at cybercrime.gov.in"
            ]
        elif "1930" in primary_doc["tags"] or "golden hour" in primary_doc["tags"]:
            response_text = (
                f"According to the **{source}** in '{title}', victims of financial cyber frauds "
                "must report instances instantly inside the 'Golden Hour' (first 2 hours). This critical window "
                "allows banks to trace and block assets from illicit accounts."
            )
            key_actions = [
                "Call 1930 immediately to freeze the recipient's transaction flows",
                "Gather UPI transaction references, receipts, and screenshot logs",
                "Submit official records at cybercrime.gov.in"
            ]
        elif "upi pin" in primary_doc["tags"] or "rbi" in primary_doc["tags"]:
            response_text = (
                f"Under the **{source}** official advisories ('{title}'), users must observe "
                "that enter of UPI PIN is mandatory only for executing debits (sending money), "
                "never for receiving cashbacks or deposits. Never submit banking access keys via SMS links."
            )
            key_actions = [
                "Never type a UPI PIN to receive money or contest fake charges",
                "Keep credits details, CVV, OTP, and net banking password credentials confidential",
                "Immediately contact the bank if security values are exposed"
            ]
        elif "trojan" in primary_doc["tags"] or "android" in primary_doc["tags"] or "cert-in" in primary_doc["tags"]:
            response_text = (
                f"The security framework from **{source}** in '{title}' highlights active "
                "Android Trojan campaigns designed to steal OTP numbers and banking parameters through "
                "screen layers or Accessibility Services access."
            )
            key_actions = [
                "Avoid installing APK packages from unknown website links or SMS channels",
                "Download apps only from trusted portals like Google Play Store or iOS App Store",
                "Review dynamic accessibility permissions required by applications"
            ]
        else:
            # General fallback using primary context summary
            response_text = (
                f"According to official advisories from the **{source}** in '{title}': "
                f"{content[:200]}..."
            )
            key_actions = [
                "Ensure verify identities before sharing personal banking access indicators",
                "Avoid clicking on external URL attachments in text prompts",
                "Report suspicious communications or callers via the national helpline 1930"
            ]

        # If a secondary context exists, append brief summary
        if len(contexts) > 1:
            sec = contexts[1]
            response_text += f"\n\nAdditionally, supplementary guidelines from the **{sec['source']}** ('{sec['title']}') note: {sec['content'][:250]}..."

        return {"response": response_text, "key_actions": key_actions}

    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Provides generalized security guidelines if direct matches are low."""
        return {
            "query": query,
            "answer": (
                "Regarding your inquiry, we did not find a direct matching official government advisory. "
                "However, as general cyber hygiene from NCRP and CERT-In: "
                "Always verify caller details through official channels. "
                "No bank or officer asks for credit card OTPs or UPI PINs to deposit money. "
                "Do not install remote terminal applications from external SMS links."
            ),
            "key_actions": [
                "Reject suspicious calls demanding digital arrest statement checks",
                "Never share passwords, credit card credentials, or OTP codes",
                "Log all instances via 1930 helpline or cybercrime.gov.in"
            ],
            "retrieved_sources": []
        }
