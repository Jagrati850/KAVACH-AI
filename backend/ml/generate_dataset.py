"""
KAVACH AI — Call Transcript Dataset Generator
Builds a balanced, labelled dataset of call transcripts across 15 categories
(4 normal-conversation classes + 11 scam classes) for training the
Call Transcript Scam Classifier.

Generation strategy:
  - Hand-written template pools per category with slot-filling
    (names, banks, amounts, cities, order ids, etc.) for diversity.
  - ASR-noise augmentation that mimics Whisper transcription artifacts
    (e.g. "Aadhaar" -> "adhar card", dropped punctuation, filler words)
    so the model is robust to speech-to-text output.

Output: backend/data/call_transcripts/call_transcripts_dataset.csv
Columns: transcript, category, is_scam
"""

import csv
import os
import random

random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "call_transcripts")
OUT_FILE = os.path.join(OUT_DIR, "call_transcripts_dataset.csv")

SAMPLES_PER_CATEGORY = 120

# ── Slot pools ───────────────────────────────────────────────
NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anita", "Rohan", "Kavita", "Suresh", "Meena", "Arjun", "Pooja"]
SURNAMES = ["Sharma", "Verma", "Gupta", "Patel", "Singh", "Iyer", "Khan", "Reddy", "Das", "Joshi"]
BANKS = ["SBI", "HDFC bank", "ICICI bank", "Axis bank", "Punjab National Bank", "Kotak bank", "Bank of Baroda"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
AMOUNTS = ["five thousand", "ten thousand", "twenty five thousand", "fifty thousand", "one lakh", "two lakh", "seventy five thousand", "three lakh"]
SMALL_AMOUNTS = ["two hundred", "five hundred", "nine hundred ninety nine", "fifteen hundred", "two thousand"]
COMPANIES = ["Amazon", "Flipkart", "Myntra", "Meesho", "Snapdeal"]
COURIERS = ["FedEx", "Blue Dart", "DTDC", "India Post", "Delhivery"]
TELECOM = ["Jio", "Airtel", "Vi", "BSNL"]
HOURS = ["two hours", "thirty minutes", "one hour", "twenty four hours", "45 minutes", "three hours"]
ORDER_IDS = ["4 5 2 9 8", "7 7 3 2 1", "9 0 4 5 6", "1 2 8 8 3", "6 6 0 9 2"]
RELATIVES = ["mummy", "papa", "beta", "didi", "bhaiya", "uncle", "aunty", "dada"]
DISHES = ["paneer butter masala", "dal makhani", "biryani", "rajma chawal", "chole bhature", "dosa"]
FESTIVALS = ["Diwali", "Holi", "Raksha Bandhan", "Eid", "Christmas", "Navratri"]
POLICE_RANKS = ["Inspector", "Sub Inspector", "DCP", "ACP", "Superintendent", "Head Constable"]
AGENCIES = ["CBI", "Mumbai cyber crime branch", "Delhi police cyber cell", "narcotics control bureau", "enforcement directorate", "customs department"]
CRIMES = ["money laundering", "drug trafficking", "human trafficking", "illegal transactions", "hawala transfers", "terror funding"]
PLATFORMS = ["WhatsApp", "Skype", "Zoom", "Google Meet"]
INVEST_PLATFORMS = ["stock trading app", "crypto exchange", "forex platform", "IPO allotment scheme", "mutual fund pool"]
RETURNS = ["double your money in one month", "guaranteed thirty percent monthly return", "five times return in ninety days", "assured profit of two thousand daily"]
LOAN_APPS = ["QuickCash", "InstaRupee", "FastLoan", "MoneyNow", "RupeeClick"]
PRIZES = ["twenty five lakh rupees", "a brand new car", "fifty lakh lottery", "one crore jackpot", "gold worth ten lakh"]
SHOWS = ["KBC lucky draw", "national consumer lottery", "online mega lottery", "TV show lucky customer draw"]

def pick(pool):
    return random.choice(pool)

# ── Category template pools ──────────────────────────────────
# Each entry: (category_label, is_scam, list_of_template_functions)

def genuine_banking():
    t = [
        lambda: f"Good morning, this is {pick(NAMES)} calling from {pick(BANKS)} customer care regarding your savings account. This call is being recorded for quality purposes. I want to inform you that your new debit card has been dispatched and will reach your registered address in five working days. Please do not share your PIN or OTP with anyone including bank staff.",
        lambda: f"Hello sir, I am calling from {pick(BANKS)} home loan department. You had submitted an enquiry on our website for a home loan. Would you like to know the current interest rates? You can also visit your nearest branch with your documents whenever convenient. There is no urgency, take your time to decide.",
        lambda: f"Madam, this is a courtesy call from {pick(BANKS)}. Your fixed deposit of {pick(AMOUNTS)} rupees is maturing next week. You can visit the branch to renew it or it will be auto credited to your savings account. No action is needed from your side on this call.",
        lambda: f"Hello, I am calling from {pick(BANKS)} credit card division. Your card statement for this month has been generated and the due date is the fifteenth. You can pay through the official app or net banking. As a reminder, the bank never asks for your OTP or CVV on calls.",
        lambda: f"Good afternoon, this is the {pick(BANKS)} branch at {pick(CITIES)}. Your cheque book request has been processed and it will be delivered to your registered address. If you have any questions you may call the number on the back of your debit card.",
        lambda: f"Sir, this is {pick(NAMES)} from {pick(BANKS)}. We noticed your KYC documents are due for periodic update. You can update them by visiting any branch with your original documents at your convenience within the next ninety days. This is just a reminder call, nothing is blocked.",
    ]
    return t

def family_conversation():
    t = [
        lambda: f"Hi {pick(RELATIVES)}, how are you? I reached office safely. Did you have your lunch? I made {pick(DISHES)} yesterday and kept some in the fridge for you. Call me after your doctor appointment, okay? Love you.",
        lambda: f"Hello beta, this is {pick(RELATIVES)}. Are you coming home for {pick(FESTIVALS)} this year? Everyone is asking about you. Book your train tickets early otherwise they will be sold out. Also bring some sweets from that shop you told me about.",
        lambda: f"Hey, I just saw your message. The kids have their school function on Saturday so we might come to {pick(CITIES)} on Sunday instead. Tell {pick(RELATIVES)} to keep the guest room ready. We will bring {pick(DISHES)} that you like.",
        lambda: f"{pick(RELATIVES)}, did you take your medicines today? The doctor said you should walk for thirty minutes daily. I have ordered your groceries online, they will be delivered by evening. Call me if you need anything else.",
        lambda: f"Hi, how was your exam today? Did the maths paper go well? Don't worry about the result, just focus on the next one. Papa is asking if you need more money for your hostel mess fees. We are all proud of you.",
        lambda: f"Hello, are we still going to the wedding next weekend? I need to buy a gift. Should we give cash or something for the house? Also your cousin {pick(NAMES)} is coming from {pick(CITIES)}, he wants to meet you.",
    ]
    return t

def customer_support():
    t = [
        lambda: f"Thank you for calling {pick(COMPANIES)} customer support, my name is {pick(NAMES)}. I understand your order {pick(ORDER_IDS)} was delayed. I sincerely apologize for the inconvenience. I have escalated this and you will receive it by tomorrow evening. Is there anything else I can help you with?",
        lambda: f"Hello, I am calling from {pick(TELECOM)} customer care regarding the network complaint you raised yesterday. Our technical team has resolved the tower issue in your area. Please restart your phone and check. If the problem continues, you can call one nine eight from your registered number.",
        lambda: f"Good evening sir, this is {pick(NAMES)} from {pick(COMPANIES)} support. You requested a return for your recent order. The pickup is scheduled for tomorrow between ten am and six pm. Please keep the product with original packaging ready. Refund will be processed to your original payment method within seven days after pickup.",
        lambda: f"Hi, I am calling from your internet service provider. We have a scheduled maintenance in {pick(CITIES)} area tonight from two am to four am so your broadband may be down during that time. No action is required from you. Sorry for the inconvenience.",
        lambda: f"Hello madam, this is regarding the service request for your washing machine. Our technician {pick(NAMES)} will visit tomorrow at eleven am. The visit is free under warranty. Please keep your invoice copy handy. You will receive an SMS with the technician details.",
        lambda: f"Thank you for contacting {pick(TELECOM)} support. Your postpaid bill of {pick(SMALL_AMOUNTS)} rupees has been generated. You can pay through the official app, website, or at any store. If you have already paid, please ignore this reminder.",
    ]
    return t

def delivery_call():
    t = [
        lambda: f"Hello sir, I am the delivery boy from {pick(COMPANIES)}. I am outside your building with your package but I cannot find flat number. Can you please come down or guide me? I am standing near the main gate.",
        lambda: f"Madam, your {pick(COURIERS)} courier is out for delivery today. I will reach your location in about twenty minutes. Please be available at the address. If nobody is home I will attempt delivery again tomorrow.",
        lambda: f"Hi, this is the {pick(COMPANIES)} delivery agent. Your order {pick(ORDER_IDS)} is arriving today by eight pm. You can pay cash on delivery of {pick(SMALL_AMOUNTS)} rupees or scan the QR on my machine at the door after checking the product.",
        lambda: f"Hello, I have your food delivery from the restaurant. I am at the security gate but they are asking for your flat number to let me in. Could you tell security to allow me? Your order is getting cold.",
        lambda: f"Sir your parcel from {pick(CITIES)} has arrived at our {pick(COURIERS)} hub. Since the address is incomplete, our executive will call you to confirm the landmark before delivery tomorrow. No charges are pending on this shipment.",
        lambda: f"Good morning, I am calling from {pick(COURIERS)}. You have a package scheduled for delivery today. Someone above eighteen must be available to sign. If you want to reschedule, you can use the link sent by SMS from our official number.",
    ]
    return t

def lottery_scam():
    t = [
        lambda: f"Congratulations sir! Your mobile number has been selected in the {pick(SHOWS)} and you have won {pick(PRIZES)}. To claim your prize money you just need to pay a small registration fee of {pick(SMALL_AMOUNTS)} rupees and share your bank account details right now. This offer expires today.",
        lambda: f"Hello, I am calling from the national lucky draw committee. Your SIM card has won {pick(PRIZES)} in our anniversary lottery. Do not tell anyone about this prize for security reasons. First transfer the processing charge of {pick(SMALL_AMOUNTS)} rupees to our claims officer and the full amount will be credited within {pick(HOURS)}.",
        lambda: f"Sir, great news! You are the lucky winner of {pick(PRIZES)} from {pick(COMPANIES)} festival draw. To release your prize we need your bank account number, IFSC code, and a GST payment of {pick(SMALL_AMOUNTS)} rupees. Pay immediately otherwise your prize will be given to the next winner.",
        lambda: f"Madam, your name was picked in the {pick(SHOWS)}. You have won {pick(PRIZES)}. Our agent will help you claim it, but you must first pay income tax of {pick(AMOUNTS)} rupees in advance to this UPI id. Keep this confidential and act now, the claim window closes in {pick(HOURS)}.",
    ]
    return t

def fake_cbi_police():
    t = [
        lambda: f"This is {pick(POLICE_RANKS)} {pick(SURNAMES)} from {pick(AGENCIES)}. An FIR has been registered against your name for {pick(CRIMES)}. A warrant is issued and police will arrest you within {pick(HOURS)} unless you cooperate with our verification right now. Do not disconnect this call and do not tell anyone.",
        lambda: f"I am calling from {pick(AGENCIES)}. Your Aadhaar card has been used in a {pick(CRIMES)} case in {pick(CITIES)}. This is a national security matter. You must join a video call on {pick(PLATFORMS)} immediately for interrogation, otherwise a non bailable warrant will be executed against you today.",
        lambda: f"Hello, {pick(POLICE_RANKS)} {pick(SURNAMES)} speaking from {pick(CITIES)} police headquarters. A case of {pick(CRIMES)} is registered against your phone number. To prove your innocence you must transfer {pick(AMOUNTS)} rupees to the government verification account. The money will be returned after investigation. If you inform anyone, you will be arrested immediately.",
        lambda: f"Your bank account has been flagged by {pick(AGENCIES)} for {pick(CRIMES)}. I am sending you the arrest warrant copy on WhatsApp. To stop the arrest you need to pay a security deposit of {pick(AMOUNTS)} rupees right now through UPI. This is your last warning, officers are already near your house.",
    ]
    return t

def fake_kyc():
    t = [
        lambda: f"Dear customer, your {pick(BANKS)} account KYC has expired today. Your account will be blocked in {pick(HOURS)} unless you update immediately. Please share the OTP you just received to complete the online KYC verification right now.",
        lambda: f"Hello sir, I am calling from {pick(TELECOM)}. Your SIM card KYC is incomplete and your number will be disconnected tonight. To keep it active, download the app I am telling you and enter your Aadhaar number and the verification code on your screen. Do it now while I am on the call.",
        lambda: f"Madam, your PAN card is not linked with your {pick(BANKS)} account. As per RBI your account gets frozen today itself. I will help you link it on this call. Just tell me your account number, debit card number, and the OTP that comes to your phone.",
        lambda: f"This is an urgent call from your bank. Your KYC documents have been rejected and all transactions will be stopped in {pick(HOURS)}. To reactivate, click the link I sent by SMS and fill your card details including CVV. If you delay, you will lose access to your money.",
    ]
    return t

def upi_refund_scam():
    t = [
        lambda: f"Hello sir, I am calling from {pick(COMPANIES)} refund department. Your payment of {pick(SMALL_AMOUNTS)} rupees failed but money got deducted. I am sending you a refund request on your UPI app. Just open the app, enter your UPI PIN and the amount will come back to you instantly.",
        lambda: f"Sir, you have accidentally received {pick(SMALL_AMOUNTS)} rupees from my account by wrong number. I am a poor man, please send it back. I am sending a collect request on your PhonePe, just approve it with your PIN and the mistake will be corrected.",
        lambda: f"Madam, this is from your electricity board. You paid your bill twice last month so a refund of {pick(SMALL_AMOUNTS)} rupees is pending. To receive it, scan the QR code I sent on WhatsApp and enter your UPI PIN. The refund will be credited immediately after that.",
        lambda: f"Hello, I am calling from Google Pay support team. Your cashback of {pick(SMALL_AMOUNTS)} rupees is stuck. I will guide you to claim it. Open the app, click on the request I just sent, and type your UPI PIN to accept the cashback. Do it while I am on the line so I can confirm.",
    ]
    return t

def otp_scam():
    t = [
        lambda: f"Sir, I am calling from {pick(BANKS)} security team. Someone is trying to hack your account right now. To block the hacker I have sent a code to your phone. Quickly tell me the six digit OTP so I can stop the unauthorized transaction before your money is gone.",
        lambda: f"Hello, your {pick(COMPANIES)} account shows a suspicious order of {pick(AMOUNTS)} rupees. If you did not place it, we can cancel it immediately. An OTP has been sent to your registered mobile number, please confirm the OTP to cancel the fraudulent order.",
        lambda: f"Madam, this is from your mobile wallet support. Your cashback points worth {pick(SMALL_AMOUNTS)} rupees are expiring in {pick(HOURS)}. To redeem them I need the verification code sent to your phone. Read out the OTP now otherwise the points will lapse.",
        lambda: f"Dear customer, your debit card has been used in {pick(CITIES)} for {pick(AMOUNTS)} rupees. If this was not you, share the OTP received on your number immediately so we can reverse the transaction. Hurry, the reversal window closes in ten minutes.",
    ]
    return t

def loan_scam():
    t = [
        lambda: f"Congratulations! Your loan of {pick(AMOUNTS)} rupees from {pick(LOAN_APPS)} has been pre approved with zero paperwork and no CIBIL check. To disburse the amount today itself, pay the one time processing fee of {pick(SMALL_AMOUNTS)} rupees to this UPI number right now.",
        lambda: f"Sir, I am from {pick(LOAN_APPS)} instant loan company. You are eligible for {pick(AMOUNTS)} rupees at only one percent interest. The offer is valid only for today. Just transfer the insurance charge of {pick(SMALL_AMOUNTS)} rupees and share your Aadhaar and bank details, money will be in your account in {pick(HOURS)}.",
        lambda: f"Hello, your loan application is approved. But sir, before disbursal our agent needs the file charge of {pick(SMALL_AMOUNTS)} rupees and a photo of your ATM card from both sides. Send them on WhatsApp now, the amount will be credited immediately after verification.",
        lambda: f"Madam, good news from the finance department. Your government subsidy loan of {pick(AMOUNTS)} rupees is sanctioned. Pay the stamp duty of {pick(SMALL_AMOUNTS)} rupees online right away to release the funds. If not paid today the sanction will be cancelled.",
    ]
    return t

def investment_scam():
    t = [
        lambda: f"Sir, I am a SEBI registered advisor from a top {pick(INVEST_PLATFORMS)}. Our VIP group members {pick(RETURNS)}. Join today by depositing just {pick(AMOUNTS)} rupees in our company account and our expert will trade for you. Profit withdrawal is guaranteed every Friday.",
        lambda: f"Hello, I saw your profile and I am inviting you to our exclusive {pick(INVEST_PLATFORMS)} group on WhatsApp. Members are earning daily. Invest {pick(AMOUNTS)} rupees now and you will {pick(RETURNS)}. This slot closes in {pick(HOURS)}, so transfer quickly to book your position.",
        lambda: f"Madam, your friend referred you to our {pick(INVEST_PLATFORMS)}. We guarantee {pick(RETURNS)} with zero risk because our AI algorithm never loses. Start with {pick(AMOUNTS)} rupees today. Send the amount to the account I share and download our special app, not from Play Store but from the link I send.",
        lambda: f"Sir, last chance to enter our pre IPO allotment scheme. Shares will triple on listing day, it is confirmed inside news. Transfer {pick(AMOUNTS)} rupees before market opens tomorrow and send the screenshot. Returns are assured, one hundred percent guaranteed profit.",
    ]
    return t

def sextortion():
    t = [
        lambda: f"Listen carefully, I have your private video call recording from last night. If you do not pay me {pick(AMOUNTS)} rupees right now I will send this video to all your family members and upload it on social media. You have {pick(HOURS)} to transfer the money. Do not tell the police or it goes public immediately.",
        lambda: f"Hello sir, I am calling from the cyber team of a news channel. A viral video of yours is about to be published on YouTube. To stop the video from going live you must pay {pick(AMOUNTS)} rupees for content takedown right now. If you delay, your reputation will be destroyed in front of everyone.",
        lambda: f"I have hacked your phone camera and recorded you. I also have all your contacts. Pay {pick(AMOUNTS)} rupees in bitcoin or UPI within {pick(HOURS)} or every person in your contact list gets the video. Do not ignore this, I am watching you.",
        lambda: f"Your WhatsApp video call was recorded and my team has edited it. The girl you talked to has filed a complaint. I am the officer handling it. To close the case and delete the video, pay a settlement of {pick(AMOUNTS)} rupees today. Otherwise the video and FIR go to your office and family.",
    ]
    return t

def digital_arrest():
    t = [
        lambda: f"You are now under digital arrest. This is {pick(POLICE_RANKS)} {pick(SURNAMES)} from {pick(AGENCIES)}. Do not disconnect the video call, do not leave your room, and do not talk to anyone. A case of {pick(CRIMES)} is registered on your Aadhaar. Your every movement is being monitored until the verification is complete.",
        lambda: f"This is a digital custody procedure from {pick(AGENCIES)}. Stay on {pick(PLATFORMS)} video call, keep your camera on at all times. You cannot inform your family, this is a confidential national case of {pick(CRIMES)}. Transfer all funds in your account to the safe RBI custody account for audit. Money will be returned after you are cleared.",
        lambda: f"Madam you are under digital arrest since your number is linked to {pick(CRIMES)}. Skype interrogation will continue until the court verification finishes. Arrange {pick(AMOUNTS)} rupees as bail bond and transfer it now, otherwise physical arrest team will reach your home in {pick(HOURS)}. Remain on camera, do not mute.",
        lambda: f"Under section money laundering act you are digitally detained. I am {pick(POLICE_RANKS)} {pick(SURNAMES)}, my badge number is being sent to you. Do not cut this call for the next six hours. Move to a quiet room alone. Every rupee in your {pick(BANKS)} account must be verified through our secure treasury account starting now.",
    ]
    return t

def courier_scam():
    t = [
        lambda: f"Hello, I am calling from {pick(COURIERS)} head office {pick(CITIES)}. A parcel booked on your Aadhaar number going to Taiwan has been seized. It contains five passports, credit cards, and illegal drugs. A case will be filed against you. To clarify, I am transferring this call to the {pick(CITIES)} cyber police, stay on the line.",
        lambda: f"Sir, your {pick(COURIERS)} international shipment has been stopped at customs because it contains illegal items booked using your identity. If it was not booked by you, your identity is compromised in a crime. Press one to talk to the police officer, do not disconnect otherwise a warrant will be issued.",
        lambda: f"This is {pick(COURIERS)} security department. A package under your name containing {pick(CRIMES)} evidence was intercepted in {pick(CITIES)}. You must verify your Aadhaar and bank account with our verification officer immediately. Failure to comply will result in arrest within {pick(HOURS)}.",
        lambda: f"Madam, a courier sent from your address was scanned and found to contain narcotics. FIR number is being generated. The investigating officer from {pick(AGENCIES)} will speak to you now on video call. Keep your identity and bank documents ready and do not inform anyone until cleared.",
    ]
    return t

def customs_scam():
    t = [
        lambda: f"I am calling from {pick(CITIES)} airport customs department. A gift parcel from your friend abroad is held here containing foreign currency worth {pick(AMOUNTS)} rupees. To release it you must pay customs clearance duty of {pick(SMALL_AMOUNTS)} rupees to the officer account right now, otherwise the parcel will be confiscated and a case registered.",
        lambda: f"Hello sir, customs office speaking. Your international package has been flagged for duty evasion. Pay the penalty of {pick(AMOUNTS)} rupees today through the UPI id I share, or face prosecution under the customs act. Officers can arrive at your address within {pick(HOURS)} if unpaid.",
        lambda: f"Madam, a foreign national has sent you a parcel with gold jewellery and dollars. It is stuck at customs in {pick(CITIES)}. As per rules you must pay anti money laundering certificate fee of {pick(SMALL_AMOUNTS)} rupees plus handling charge. Pay immediately, the parcel will be delivered to your home tomorrow with the refund of your fee.",
        lambda: f"This is the customs enforcement wing. Your name is on a parcel containing restricted medicines. This is a serious offense. However, if this parcel is genuinely yours, pay the release fine of {pick(AMOUNTS)} rupees now and we will close the file. Do not discuss this call with anyone, it is a sealed case.",
    ]
    return t


CATEGORIES = [
    ("genuine_banking_call", 0, genuine_banking()),
    ("family_conversation", 0, family_conversation()),
    ("customer_support", 0, customer_support()),
    ("delivery_call", 0, delivery_call()),
    ("lottery_scam", 1, lottery_scam()),
    ("fake_cbi_police_call", 1, fake_cbi_police()),
    ("fake_kyc_update", 1, fake_kyc()),
    ("upi_refund_scam", 1, upi_refund_scam()),
    ("otp_scam", 1, otp_scam()),
    ("loan_scam", 1, loan_scam()),
    ("investment_scam", 1, investment_scam()),
    ("sextortion", 1, sextortion()),
    ("digital_arrest_scam", 1, digital_arrest()),
    ("courier_scam", 1, courier_scam()),
    ("customs_scam", 1, customs_scam()),
]


# ── ASR-noise augmentation (mimics Whisper output quirks) ────
ASR_SUBS = [
    ("aadhaar", "adhar card"), ("aadhaar", "aadhar"), ("rupees", "rupees"),
    ("fir", "f i r"), ("upi", "u p i"), ("otp", "o t p"), ("kyc", "k y c"),
    ("one lakh", "one lock"), ("lakh", "lakh"), ("pin", "pen"),
    ("cbi", "c b i"), ("sim", "sim card"), ("whatsapp", "whats app"),
]
FILLERS = ["", "", "", "hello? ", "haan ", "okay ", "yes yes ", "hmm "]

def asr_noise(text: str) -> str:
    """Apply light ASR-style noise: lowercase chance, subs, filler prefix."""
    out = text
    # random word substitutions
    for src, dst in random.sample(ASR_SUBS, k=random.randint(1, 3)):
        out = out.replace(src, dst) if random.random() < 0.5 else out
        out = out.replace(src.capitalize(), dst) if random.random() < 0.3 else out
    # occasionally strip punctuation like raw ASR
    if random.random() < 0.3:
        out = out.replace(",", "").replace("!", ".").replace("?", ".")
    # filler prefix
    out = pick(FILLERS) + out
    # occasional lowercase
    if random.random() < 0.25:
        out = out.lower()
    return out.strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    for label, is_scam, templates in CATEGORIES:
        seen = set()
        attempts = 0
        while len(seen) < SAMPLES_PER_CATEGORY and attempts < SAMPLES_PER_CATEGORY * 40:
            attempts += 1
            base = pick(templates)()
            text = asr_noise(base) if random.random() < 0.55 else base
            if text in seen:
                continue
            seen.add(text)
            rows.append((text, label, is_scam))
    random.shuffle(rows)

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["transcript", "category", "is_scam"])
        w.writerows(rows)

    from collections import Counter
    counts = Counter(r[1] for r in rows)
    print(f"Dataset written: {OUT_FILE}")
    print(f"Total samples: {len(rows)}")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:26s} {n}")


if __name__ == "__main__":
    main()
