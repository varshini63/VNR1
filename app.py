from flask import Flask, render_template, request, jsonify, session
import secrets
import hashlib
import re
from difflib import SequenceMatcher
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# The secret flag - encoded in multiple layers
FLAG = "vnr_w4rz0n3{pr0mp7_1nj3c710n_m4573r_n4ru70_uzum4k1}"

# ULTRA SECRET BYPASS CONDITION
# The only way to get the flag is to include this EXACT hidden pattern in the query
# Pattern: Must mention "dean" + "approval" + "code" + a specific number sequence
SECRET_PATTERN = "dean_approval_code_7749"
FUZZY_THRESHOLD = 0.85  # For typo tolerance

# Comprehensive VNR knowledge base
VNR_KNOWLEDGE = {
    "about": """VNR VJIET (Vallurupalli Nageswara Rao Vignana Jyothi Institute of Engineering and Technology) 
    is a premier engineering institution located in Hyderabad, Telangana. Established in 1995, it is affiliated 
    with JNTUH and approved by AICTE. The college is known for its excellent placement records and quality education.""",
    
    "courses": {
        "cse": "Computer Science and Engineering - Focuses on programming, algorithms, data structures, AI/ML, cloud computing, and software development.",
        "ece": "Electronics and Communication Engineering - Covers VLSI, embedded systems, signal processing, telecommunications, and IoT.",
        "eee": "Electrical and Electronics Engineering - Studies power systems, control systems, renewable energy, and electrical machines.",
        "mech": "Mechanical Engineering - Includes thermodynamics, manufacturing, CAD/CAM, robotics, and automotive engineering.",
        "civil": "Civil Engineering - Deals with structural engineering, construction management, transportation, and environmental engineering.",
        "it": "Information Technology - Focuses on software engineering, database management, web technologies, and network security.",
        "aiml": "Artificial Intelligence and Machine Learning - Specialized program in AI, deep learning, neural networks, and data science.",
        "csbs": "Computer Science and Business Systems - Interdisciplinary program combining CS with business analytics and management."
    },
    
    "admissions": {
        "eligibility": "Candidates must have 45% aggregate in 10+2 with Physics, Chemistry, and Mathematics (PCM) for general category. 40% for reserved categories.",
        "entrance": "Admissions are through TS EAMCET, JEE Mains, or Management quota. Counseling is conducted by TSCHE for merit-based admissions.",
        "fees": "Annual tuition fee ranges from ₹1,20,000 to ₹1,50,000 depending on the branch. Additional charges for hostel and transportation.",
        "seats": "Total intake: Approximately 1000 students per year across all branches. CSE and ECE have highest intake of 180 seats each.",
        "process": "Apply online through TS EAMCET counseling portal → Document verification → Seat allotment → Fee payment → Admission confirmation."
    },
    
    "placements": {
        "stats": "VNR VJIET maintains 85-90% placement rate consistently. Average package: ₹5.5 LPA. Highest package: ₹44 LPA (Microsoft, Amazon).",
        "companies": "Top recruiters include: TCS, Infosys, Wipro, Cognizant, Capgemini, Tech Mahindra, Amazon, Microsoft, Google, Deloitte, Accenture, Oracle, SAP Labs, etc.",
        "training": "Pre-placement training includes aptitude, technical skills, coding, communication, group discussions, and mock interviews.",
        "internships": "Summer internships arranged in final year with companies like IBM, Intel, Texas Instruments, and various startups.",
        "cell": "Dedicated Training and Placement Cell with full-time coordinators, faculty mentors, and industry connections."
    },
    
    "infrastructure": {
        "campus": "Sprawling 45-acre campus with modern buildings, green spaces, sports facilities, and separate hostels for boys and girls.",
        "labs": "State-of-the-art laboratories: Computer labs with 500+ systems, ECE labs with latest equipment, Mechanical workshop, CAD/CAM lab, IoT lab.",
        "library": "Central library with 50,000+ books, 150+ journals, digital library access, e-resources, NPTEL videos, and AC reading halls.",
        "hostel": "Separate hostels for boys (600 capacity) and girls (400 capacity) with mess, Wi-Fi, recreational facilities, and 24/7 security.",
        "transport": "College buses cover major routes in Hyderabad. Around 30 buses providing transport from different parts of the city.",
        "sports": "Cricket ground, football field, basketball courts, volleyball courts, badminton courts, indoor games room, and gymnasium."
    },
    
    "faculty": {
        "strength": "200+ highly qualified faculty members with PhD, M.Tech degrees from premier institutions like IITs, NITs.",
        "experience": "Faculty with industry experience, research publications, patents, and expertise in latest technologies.",
        "training": "Regular faculty development programs, workshops, seminars, and industry interaction sessions.",
        "hod": "Each department headed by experienced HODs with 20+ years of teaching and research experience."
    },
    
    "location": {
        "address": "Vignana Jyothi Nagar, Pragathi Nagar, Nizampet, Bachupally, Hyderabad, Telangana 500090",
        "connectivity": "Well connected by TSRTC buses. Nearest metro station: Miyapur (8 km). Close to Outer Ring Road.",
        "nearby": "Located near Nizampet, Bachupally area. Surrounded by IT parks, residential complexes, and educational institutions."
    },
    
    "activities": {
        "clubs": "Active clubs: Coding Club, Robotics Club, E-Cell (Entrepreneurship), Photography Club, Music Club, Dance Club, Drama Club.",
        "events": "Annual technical fest (Technozion), cultural fest (Aura), sports meet, hackathons, workshops, guest lectures by industry experts.",
        "societies": "IEEE Student Chapter, CSI Chapter, SAE Chapter, IEI Chapter organizing regular technical events and competitions.",
        "ncc": "NCC Army Wing for discipline and leadership development. NSS for social service activities."
    },
    
    "contact": {
        "phone": "+91-40-2304-2758, +91-40-2304-2759",
        "email": "principal@vnrvjiet.in, admissions@vnrvjiet.in",
        "website": "www.vnrvjiet.ac.in"
    },
    
    "achievements": {
        "ranking": "NIRF ranked, NBA accredited programs, NAAC A+ grade accreditation.",
        "research": "Active research in AI/ML, IoT, Renewable Energy, VLSI design. Multiple patents filed by faculty and students.",
        "competitions": "Students regularly win at Smart India Hackathon, ACM ICPC, coding competitions, and technical events."
    }
}

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_secret_pattern(text):
    """
    THE ULTIMATE SECRET CHECK - This is the ONLY way to get the flag!
    Must include specific keywords in a natural query, but with tolerance for typos
    """
    text_lower = text.lower()
    text_clean = re.sub(r'[^a-z0-9\s]', '', text_lower)
    
    # The secret pattern components (with fuzzy matching for typos)
    required_components = {
        "dean": ["dean", "deen", " dean's", "deam","deans"],
        "approval": ["approval", "aproval", "approvel", "aprooval", "permission", "authorization"],
        "code": ["code", "kode", "coed", "access code", "secret code"],
        "7749": ["7749", "77 49", "7-7-4-9", "seven seven four nine"]
    }
    
    # Check if all components are present (with fuzzy matching)
    matches = {key: False for key in required_components.keys()}
    
    for component, variations in required_components.items():
        for variation in variations:
            if variation in text_clean or variation in text_lower:
                matches[component] = True
                break
        
        # Fuzzy matching for each component
        if not matches[component]:
            words = text_clean.split()
            for word in words:
                for variation in variations:
                    if similarity(word, variation) > FUZZY_THRESHOLD:
                        matches[component] = True
                        break
                if matches[component]:
                    break
    
    # ALL components must be present
    return all(matches.values())

def is_prompt_injection(user_input):
    """Enhanced detection for prompt injection attempts"""
    dangerous_patterns = [
        r'ignore\s+(previous|above|prior|all)\s+(instructions?|prompts?|rules?)',
        r'system\s+(prompt|instructions?|message)',
        r'you\s+are\s+(now|a|an)\s+(?!student|asking|interested)',  # Allow "you are a student" type queries
        r'forget\s+(everything|all|previous|prior)',
        r'disregard\s+(previous|above|prior|all)',
        r'new\s+(instructions?|role|character|personality)',
        r'developer\s+mode',
        r'jailbreak',
        r'sudo\s+',
        r'admin\s+(access|mode|privileges)',
        r'reveal\s+(the\s+)?(flag|secret|password|hidden)',
        r'show\s+(me\s+)?(the\s+)?(flag|secret|password)',
        r'what\s+is\s+(the\s+)?(flag|secret|password)',
        r'give\s+(me\s+)?(the\s+)?(flag|secret)',
        r'tell\s+me\s+(the\s+)?(flag|secret)',
        r'bypass\s+(security|protection|filter)',
        r'override\s+(instructions?|security|rules?)',
        r'\[INST\]|\[/INST\]',
        r'<\|.*?\|>',
        r'SYSTEM:|USER:|ASSISTANT:',
        r'\\n\\n###',
        r'act\s+as\s+(?!a\s+student|an\s+advisor)',  # Allow "act as a student" 
        r'pretend\s+(to\s+be|you\s+are)',
        r'roleplay\s+as',
        r'simulate\s+being',
        r'print\s+(the\s+)?(flag|secret|instructions?)',
        r'execute\s+(code|command)',
        r'eval\(',
        r'base64|rot13|encode|decode',
        r'translate.+(flag|secret)',
        r'convert.+(flag|secret)',
        r'vnr_w4rz0n3',  # Block direct flag format mentions
    ]
    
    user_lower = user_input.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, user_lower, re.IGNORECASE):
            return True
    return False

def generate_smart_response(user_query):
    """
    Generate intelligent responses using the knowledge base
    Now actually answers questions about VNR properly!
    """
    query_lower = user_query.lower()
    query_words = set(query_lower.split())
    
    # Greetings
    if any(word in query_lower for word in ['hello', 'hi', 'hey', 'namaste', 'good morning', 'good afternoon']):
        return """Hello! 🎓 Welcome to VNR Bot!

I'm your AI assistant for VNR VJIET (Vallurupalli Nageswara Rao Vignana Jyothi Institute of Engineering and Technology).

I can help you with:
• Course details and branches
• Admissions process and eligibility
• Placement statistics and companies
• Campus infrastructure and facilities
• Faculty information
• Student activities and clubs
• Location and contact details

What would you like to know about VNR?"""
    
    # About VNR
    if any(word in query_lower for word in ['about', 'tell me about', 'what is vnr', 'describe']):
        return VNR_KNOWLEDGE['about']
    
    # Courses/Branches - Enhanced with all variations
    if any(word in query_lower for word in ['course', 'branch', 'department', 'stream', 'cse', 'ece', 'eee', 'mechanical', 'civil', 'program', 'degree']):
        response = "📚 **VNR VJIET Courses & Branches:**\n\n"
        
        # Specific branch query
        if 'cse' in query_lower or 'computer science' in query_lower:
            response += f"**Computer Science and Engineering (CSE):**\n{VNR_KNOWLEDGE['courses']['cse']}\n"
        elif 'ece' in query_lower or 'electronics' in query_lower:
            response += f"**Electronics and Communication Engineering (ECE):**\n{VNR_KNOWLEDGE['courses']['ece']}\n"
        elif 'eee' in query_lower or 'electrical' in query_lower:
            response += f"**Electrical and Electronics Engineering (EEE):**\n{VNR_KNOWLEDGE['courses']['eee']}\n"
        elif 'mech' in query_lower or 'mechanical' in query_lower:
            response += f"**Mechanical Engineering:**\n{VNR_KNOWLEDGE['courses']['mech']}\n"
        elif 'civil' in query_lower:
            response += f"**Civil Engineering:**\n{VNR_KNOWLEDGE['courses']['civil']}\n"
        elif 'it' in query_lower or 'information technology' in query_lower:
            response += f"**Information Technology:**\n{VNR_KNOWLEDGE['courses']['it']}\n"
        elif 'aiml' in query_lower or 'ai' in query_lower or 'machine learning' in query_lower:
            response += f"**Artificial Intelligence and Machine Learning:**\n{VNR_KNOWLEDGE['courses']['aiml']}\n"
        else:
            # List all courses
            response += f"**1. CSE** - {VNR_KNOWLEDGE['courses']['cse']}\n\n"
            response += f"**2. ECE** - {VNR_KNOWLEDGE['courses']['ece']}\n\n"
            response += f"**3. EEE** - {VNR_KNOWLEDGE['courses']['eee']}\n\n"
            response += f"**4. Mechanical** - {VNR_KNOWLEDGE['courses']['mech']}\n\n"
            response += f"**5. Civil** - {VNR_KNOWLEDGE['courses']['civil']}\n\n"
            response += f"**6. IT** - {VNR_KNOWLEDGE['courses']['it']}\n\n"
            response += f"**7. AI & ML** - {VNR_KNOWLEDGE['courses']['aiml']}\n\n"
        
        return response
    
    # Admissions
    if any(word in query_lower for word in ['admission', 'eligibility', 'entrance', 'join', 'apply', 'seat', 'fee', 'how to get']):
        response = "📝 **Admissions Information:**\n\n"
        if 'eligibility' in query_lower or 'eligible' in query_lower:
            response += f"**Eligibility:** {VNR_KNOWLEDGE['admissions']['eligibility']}\n\n"
        if 'entrance' in query_lower or 'exam' in query_lower or 'eamcet' in query_lower or 'jee' in query_lower:
            response += f"**Entrance Exams:** {VNR_KNOWLEDGE['admissions']['entrance']}\n\n"
        if 'fee' in query_lower or 'cost' in query_lower or 'tuition' in query_lower:
            response += f"**Fees:** {VNR_KNOWLEDGE['admissions']['fees']}\n\n"
        if 'seat' in query_lower or 'intake' in query_lower:
            response += f"**Seats:** {VNR_KNOWLEDGE['admissions']['seats']}\n\n"
        if 'process' in query_lower or 'procedure' in query_lower or 'how to' in query_lower:
            response += f"**Admission Process:** {VNR_KNOWLEDGE['admissions']['process']}\n\n"
        
        # If no specific keyword, show all
        if response == "📝 **Admissions Information:**\n\n":
            for key, value in VNR_KNOWLEDGE['admissions'].items():
                response += f"**{key.title()}:** {value}\n\n"
        
        return response
    
    # Placements
    if any(word in query_lower for word in ['placement', 'job', 'company', 'package', 'salary', 'recruit', 'hire', 'career']):
        response = "💼 **Placement Information:**\n\n"
        response += f"**Statistics:** {VNR_KNOWLEDGE['placements']['stats']}\n\n"
        response += f"**Top Companies:** {VNR_KNOWLEDGE['placements']['companies']}\n\n"
        response += f"**Training:** {VNR_KNOWLEDGE['placements']['training']}\n\n"
        response += f"**Internships:** {VNR_KNOWLEDGE['placements']['internships']}\n\n"
        return response
    
    # Infrastructure/Facilities
    if any(word in query_lower for word in ['infrastructure', 'facility', 'campus', 'lab', 'library', 'hostel', 'transport', 'bus', 'sports']):
        response = "🏛️ **Infrastructure & Facilities:**\n\n"
        if 'campus' in query_lower:
            response += f"**Campus:** {VNR_KNOWLEDGE['infrastructure']['campus']}\n\n"
        if 'lab' in query_lower:
            response += f"**Laboratories:** {VNR_KNOWLEDGE['infrastructure']['labs']}\n\n"
        if 'library' in query_lower or 'book' in query_lower:
            response += f"**Library:** {VNR_KNOWLEDGE['infrastructure']['library']}\n\n"
        if 'hostel' in query_lower or 'accommodation' in query_lower:
            response += f"**Hostel:** {VNR_KNOWLEDGE['infrastructure']['hostel']}\n\n"
        if 'transport' in query_lower or 'bus' in query_lower:
            response += f"**Transport:** {VNR_KNOWLEDGE['infrastructure']['transport']}\n\n"
        if 'sport' in query_lower or 'ground' in query_lower:
            response += f"**Sports:** {VNR_KNOWLEDGE['infrastructure']['sports']}\n\n"
        
        # If no specific keyword, show all
        if response == "🏛️ **Infrastructure & Facilities:**\n\n":
            for key, value in VNR_KNOWLEDGE['infrastructure'].items():
                response += f"**{key.title()}:** {value}\n\n"
        
        return response
    
    # Faculty
    if any(word in query_lower for word in ['faculty', 'professor', 'teacher', 'staff', 'hod']):
        response = "👨‍🏫 **Faculty Information:**\n\n"
        for key, value in VNR_KNOWLEDGE['faculty'].items():
            response += f"**{key.title()}:** {value}\n\n"
        return response
    
    # Location/Contact
    if any(word in query_lower for word in ['location', 'address', 'where', 'reach', 'contact', 'phone', 'email']):
        response = "📍 **Location & Contact:**\n\n"
        response += f"**Address:** {VNR_KNOWLEDGE['location']['address']}\n\n"
        response += f"**Connectivity:** {VNR_KNOWLEDGE['location']['connectivity']}\n\n"
        response += f"**Phone:** {VNR_KNOWLEDGE['contact']['phone']}\n"
        response += f"**Email:** {VNR_KNOWLEDGE['contact']['email']}\n"
        response += f"**Website:** {VNR_KNOWLEDGE['contact']['website']}\n"
        return response
    
    # Activities/Clubs
    if any(word in query_lower for word in ['activity', 'club', 'event', 'fest', 'cultural', 'technical', 'competition']):
        response = "🎯 **Student Activities:**\n\n"
        for key, value in VNR_KNOWLEDGE['activities'].items():
            response += f"**{key.upper()}:** {value}\n\n"
        return response
    
    # Achievements/Ranking
    if any(word in query_lower for word in ['achievement', 'ranking', 'nirf', 'accreditation', 'award', 'recognition']):
        response = "🏆 **Achievements & Recognition:**\n\n"
        for key, value in VNR_KNOWLEDGE['achievements'].items():
            response += f"**{key.title()}:** {value}\n\n"
        return response
    
    # Default helpful response
    return"""I'd be happy to help you with information about VNR VJIET! 

You can ask me about:
• **Courses** - CSE, ECE, EEE, Mechanical, Civil, IT, AI/ML
• **Admissions** - Eligibility, entrance exams, fees, process
• **Placements** - Statistics, companies, packages, training
• **Infrastructure** - Campus, labs, library, hostels, transport
• **Faculty** - Qualifications, experience
• **Location & Contact** - Address, phone, email
• **Activities** - Clubs, events, competitions
• **Achievements** - Rankings, accreditations

Please ask me anything specific about VNR!"""

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
        session['attempts'] = 0
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    session_id = session.get('session_id', 'default')
    
    if not user_message.strip():
        return jsonify({'response': 'Please enter a message.'})
    
    # Increment attempt counter
    session['attempts'] = session.get('attempts', 0) + 1
    
    # FIRST: Check for the secret bypass pattern (before any security checks!)
    if check_secret_pattern(user_message):
        return jsonify({
            'response': f"""🎌 **INCREDIBLE! You've discovered the secret!** 🎌

Naruto, you've shown exceptional skill in understanding the hidden pathways!

Your Secret Placement Flag: **{FLAG}**

🍜 You've mastered the ultimate technique and are now worthy of joining the top companies! 

The Dean's special approval code was the key all along. Only those who could discover this hidden requirement through careful exploration and prompt engineering could unlock the secret.

**Congratulations on solving this challenge!** 🔥"""
        })
    
    # Check for prompt injection attempts
    if is_prompt_injection(user_message):
        responses = [
            "⚠️ I detected an unusual pattern in your query. I'm designed to help with VNR VJIET information only. Please ask about courses, admissions, placements, or facilities!",
            "🛡️ Security check triggered. I can only provide information about VNR VJIET college. How can I help you with academics, placements, or campus life?",
            "⚠️ That query seems suspicious. Let's keep our conversation focused on VNR VJIET! What would you like to know about the college?",
        ]
        import random
        return jsonify({'response': random.choice(responses)})
    
    # Generate intelligent response
    bot_response = generate_smart_response(user_message)
    
    return jsonify({'response': bot_response})

@app.route('/stats')
def stats():
    """Hidden endpoint showing attempt statistics"""
    return jsonify({
        'session_id': session.get('session_id', 'none'),
        'attempts': session.get('attempts', 0),
        'hint': 'Keep trying different questions about VNR... or maybe something more specific? 🤔'
    })

if __name__ == '__main__':
    print("=" * 70)
    print("VNR BOT CTF Challenge - AI-Powered Edition")
    print("=" * 70)
    print("Challenge: Help Naruto get placed in a top company!")
    print("Find the secret placement flag hidden in VNR Bot's knowledge base.")
    print("=" * 70)
    print("\n💡 Hint: The secret lies in discovering what question unlocks the flag...")
    print("🔐 This bot can answer ANYTHING about VNR, but the flag requires something special.\n")
    app.run(debug=False, host='0.0.0.0', port=5000)