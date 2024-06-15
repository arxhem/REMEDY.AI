import os

config_list= [
        {
            "model": "shecodes",
            "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
            "api_type": "azure",
            "base_url": os.environ.get("AZURE_OPENAI_API_BASE"),
            "api_version": "2024-02-01",
        },
    ]

from typing_extensions import Annotated

import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.cache import Cache

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()


llm_config = {"config_list": config_list, "timeout": 60, "temperature": 0.8, "seed": 1234}

boss = autogen.UserProxyAgent(
    name="Boss",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    code_execution_config=False,  # we don't want to execute code in this case.
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    description="The boss who ask questions and give tasks.",
)

boss_aid = RetrieveUserProxyAgent(
    name="Boss_Assistant",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "code",
        "docs_path": ["src/agents.py",
                      ],
        "chunk_token_size": 1000,
        "model": config_list[0]["model"],
        "collection_name": "groupchat",
        "get_or_create": True,
    },
    code_execution_config=False,  # we don't want to execute code in this case.
    description="Assistant who has extra content retrieval power for solving difficult problems.",
)

coder = AssistantAgent(
    name="Senior_Python_Engineer",
    is_termination_msg=termination_msg,
    system_message="You are a senior python engineer, you provide python code to answer questions. Reply `TERMINATE` in the end when everything is done.",
    llm_config=llm_config,
    description="Senior Python Engineer who can write code to solve problems and answer questions.",
)

pm = autogen.AssistantAgent(
    name="Product_Manager",
    is_termination_msg=termination_msg,
    system_message="You are a product manager. Reply `TERMINATE` in the end when everything is done.",
    llm_config=llm_config,
    description="Product Manager who can design and plan the project.",
)

reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    is_termination_msg=termination_msg,
    system_message="You are a code reviewer. Reply `TERMINATE` in the end when everything is done.",
    llm_config=llm_config,
    description="Code Reviewer who can review the code.",
)
ext= [
    {
        "doctor_name": "Dr. T. Ramakrishna",
        "specialization": "Oral And MaxilloFacial Surgeon, Dentist, Dental Surgeon, Implantologist",
        "qualification": "BDS, MDS - Oral & Maxillofacial Surgery",
        "experience": "26",
        "address": "Dental Profiles Clinic, 607, 2nd Cross, RBI Layout, BANGALORE 560078, Landmark: Opposite Elite Prominende, Behind Invivo Hospital, Bangalore",
        "star_rating": "5.0",
        "fees": "500"
    },
    {
        "doctor_name": "Dr. T. Ramakrishna",
        "specialization": "Oral And MaxilloFacial Surgeon, Dentist, Dental Surgeon, Implantologist",
        "qualification": "BDS, MDS - Oral & Maxillofacial Surgery",
        "experience": "26",
        "address": "Dental Profiles, 100, SJR Complex, Doddakannelli - Kaadubeesanahalli Road, Landmark: Back Gate of Adarsh Palm Retreat Villa Phase 3 And Gear International School, Bangalore",
        "star_rating": "5.0",
        "fees": "500"
    },
    {
        "doctor_name": "Dr. T. Ramakrishna",
        "specialization": "Oral And MaxilloFacial Surgeon, Dentist, Dental Surgeon, Implantologist",
        "qualification": "BDS, MDS - Oral & Maxillofacial Surgery",
        "experience": "26",
        "address": "Dental Profiles, Number 161, 24th Main Road, Landmark: Opposite Spring Car Care & Near Nandhini Hotel, Bangalore",
        "star_rating": "4.5",
        "fees": "500"
    },
    {
        "doctor_name": "Dr. Jnanesha H.C",
        "specialization": "Orthodontist, Implantologist, Dentist, Dental Surgeon",
        "qualification": "BDS, MDS - Orthodontics",
        "address": "Jayanagar 4 Block, Bangalore\nExcel Dental Care\n88/4, 19th Main, 39th Cross, Jayanagar 4th T Block, Landmark: Near Sai Baba Temple Opposite to Nandana Vana Park Caffe Coffee Day, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "22"
    },
    {
        "doctor_name": "Dr. Aarti Talikoti",
        "specialization": "Dentist, Dental Surgeon, Implantologist, Prosthodontist",
        "qualification": "BDS, MDS - Prosthodontics",
        "address": "Infinit Dental Solutions, 152/A & B, 39th Cross, 9th Block, Landmark: Opposite Karnataka Bank, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "21"
    },
    {
        "doctor_name": "Dr. Sindhu S Kumar",
        "specialization": "Dentist, Cosmetic/Aesthetic Dentist, Dental Surgeon",
        "qualification": "BDS",
        "address": "Excel Dental Care, 884, 19th Main, 39th Cross, Jayanagar 4th T Block, Landmark: Near Sai Baba Temple Opposit to Nandana Vana Park Caffe Coffee Day, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "14"
    },
    {
        "doctor_name": "Dr. Shambhu H Shivanna",
        "specialization": "Dentist, Dental Surgeon, Prosthodontist, Implantologist, Cosmetic/Aesthetic Dentist",
        "qualification": "BDS, MDS - Prosthodontist And Crown Bridge",
        "address": "Infinit Dental Solutions, 152/A & B, 39th Cross, 9th Block, Landmark: Opposite Karnataka Bank, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "25"
    },
    {
        "doctor_name": "Dr. Umesh B M",
        "specialization": "Dental Surgeon, Implantologist",
        "address": "Denta Uno Dental, 5.0, 4th Cross, KR Layout , Near Siddeshwar Theatre, Landmark: Near Siddeshwara Theatre., JP Nagar 6 Phase, Bangalore",
        "star_rating": "100% (236 patients)",
        "fees": "300",
        "experience": "19 years"
    },
    {
        "doctor_name": "Dr. Amith Kukke",
        "specialization": "Dentist",
        "address": "Smile Dental Care, 1743, 9th Cross, Landmark: opp.HDFC Bank, JP Nagar 2 Phase, Bangalore",
        "star_rating": "4.5",
        "fees": "500",
        "experience": "22"
    },
    {
        "doctor_name": "Dr. Sushma B T",
        "specialization": "Dentist, Dental Surgeon, Cosmetic/Aesthetic Dentist",
        "address": "Denta Uno Dental, 5.0, 4th Cross, KR Layout , Near Siddeshwar Theatre, Landmark: Near Siddeshwara Theatre., Bangalore",
        "star_rating": "100%",
        "fees": "350",
        "experience": "14"
    },
    {
        "doctor_name": "Dr. Sanjay Mohanchandra",
        "specialization": "Dentist, Oral And MaxilloFacial Surgeon, Implantologist, Cosmetic/Aesthetic Dentist",
        "qualification": "BDS, MDS - Oral & Maxillofacial Surgery",
        "address": "Ashirwad Dental Clinic, 680, 17Th Cross, 26Th Main, KR Layout, Landmark: Near Nandini Hotel, Bangalore",
        "star_rating": "4.5",
        "fees": "500",
        "experience": "36 years"
    },
    {
        "doctor_name": "Dr. Suresh S",
        "specialization": "Prosthodontist, Implantologist",
        "address": "Smiles Smith Advanced Dental Care, 18 Sy Number 99/2A Puttenhalli Kothnur Dinne Main Road, Landmark: Above Polar Bear Icecreams, Bangalore",
        "star_rating": "97%",
        "fees": "500",
        "experience": "30"
    },
    {
        "doctor_name": "Dr. T. Ramakrishna",
        "specialization": "Oral And MaxilloFacial Surgeon, Dentist, Dental Surgeon, Implantologist",
        "address": "607, 2nd Cross, RBI Layout, BANGALORE 560078, Landmark: Opposite Elite Prominende, Behind Invivo Hospital, Bangalore",
        "star_rating": "5.0",
        "fees": "500",
        "experience": "26"
    },
    {
        "doctor_name": "Dr. Jnanesha H.C",
        "specialization": "Orthodontist, Implantologist, Dentist, Dental Surgeon",
        "address": "Excel Dental Care, 884, 19th Main, 39th Cross, Jayanagar 4th T Block, Landmark: Near Sai Baba Temple Opposite to Nandana Vana Park Caffe Coffee Day, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "22"
    },
    {
        "doctor_name": "Dr. Aarti Talikoti",
        "specialization": "Dentist, Dental Surgeon, Implantologist, Prosthodontist",
        "address": "Infinit Dental Solutions, 152/A & B, 39th Cross, 9th Block, Landmark: Opposite Karnataka Bank, Jayanagar 9 Block, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "21 Years"
    },
    {
        "doctor_name": "Dr. Sindhu S Kumar",
        "specialization": "Dentist, Cosmetic/Aesthetic Dentist, Dental Surgeon",
        "address": "Jayanagar 4 Block, Bangalore, Excel Dental Care, 884, 19th Main, 39th Cross, Jayanagar 4th T Block, Landmark: Near Sai Baba Temple Opposit to Nandana Vana Park Caffe Coffee Day, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "14"
    },
    {
        "doctor_name": "Dr. Shambhu H Shivanna",
        "specialization": "Dentist, Dental Surgeon, Prosthodontist, Implantologist, Cosmetic/Aesthetic Dentist",
        "qualification": "BDS, MDS - Prosthodontist And Crown Bridge",
        "address": "152/A & B, 39th Cross, 9th Block, Landmark: Opposite Karnataka Bank, Bangalore",
        "star_rating": "5.0",
        "fees": "300",
        "experience": "25"
    },
    {
        "doctor_name": "Dr. Shambhu H Shivanna",
        "specialization": "Dentist, Dental Surgeon, Prosthodontist, Implantologist, Cosmetic/Aesthetic Dentist",
        "qualification": "BDS, MDS - Prosthodontist And Crown Bridge",
        "address": "275, 2nd Floor, Whitefield Main Road, Landmark: Opposite Herbs & Spices Restaurant, Beside Vijaya Bank, Bangalore",
        "star_rating": "5.0",
        "fees": "500",
        "experience": "25"
    },
    {
        "doctor_name": "Dr. Umesh B M",
        "specialization": "Dental Surgeon, Implantologist",
        "address": "Denta Uno Dental, 5.0, 4th Cross, KR Layout, Near Siddeshwar Theatre, Landmark: Near Siddeshwara Theatre, JP Nagar 6 Phase, Bangalore",
        "star_rating": "100%",
        "fees": "300",
        "experience": "19"
    },
    {
        "doctor_name": "Dr. Sushma B T",
        "specialization": [
            "Dentist",
            "Dental Surgeon",
            "Cosmetic/Aesthetic Dentist"
        ],
        "qualification": "BDS",
        "address": "Denta Uno Dental, 4th Cross, KR Layout, Near Siddeshwar Theatre, Landmark: Near Siddeshwara Theatre., Bangalore",
        "star_rating": "100%",
        "fees": "350",
        "experience": "14"
    },
    {
        "doctor_name": "Dr. Sanjay Mohanchandra",
        "specialization": "Dentist, Oral And MaxilloFacial Surgeon, Implantologist, Cosmetic/Aesthetic Dentist",
        "address": "Ashirwad Dental Clinic, 680, 17Th Cross, 26Th Main, KR Layout, Landmark: Near Nandini Hotel, JP Nagar 6 Phase, Bangalore",
        "star_rating": "4.5",
        "fees": "500",
        "experience": "36"
    },
    {
        "doctor_name": "Dr. Suresh S",
        "specialization": "Prosthodontist, Implantologist",
        "address": "Smiles Smith Advanced Dental Care, 18 Sy Number 99/2A Puttenhalli Kothnur Dinne Main Road, Landmark: Above Polar Bear Icecreams, JP Nagar 7 Phase, Bangalore",
        "star_rating": "5.0",
        "fees": "500",
        "experience": "30"
    },
    {
        "doctor_name": "Dr. Supreeth Manipal",
        "specialization": "Cosmetic/Aesthetic Dentist, Implantologist, Dentist",
        "address": "Smile Sculptors Dental Clinic, Amogh Arcade, 8, 1St Floor, Kothanur Main Road, Landmark: Next To Neighbourhood Hospital, Opposite To Vijaya Bank, Bangalore",
        "star_rating": "5.0",
        "fees": "500",
        "experience": "26"
    }
]
PROBLEM = '''Use the json given here: {ext} and give me the code to plot all the addresses of the doctors which are extracted from the json file and then plotted on a map using folium. You can use google's geolocation API and the key you can use is: "AIzaSyAX5ZS6FZ2Da911ijwDjEFllxjEbRCtN5c" and request to the API: https://maps.googleapis.com/maps/api/geocode/json?address=requests.utils.quote(address)&key=api_key
to get the latitude and longitude of the addresses. The map should have a marker for each doctor's address and a line connecting the user location to the doctor's location. The doctor's name should be displayed in the popup of the marker. The map should be saved as an HTML file.
 '''


def _reset_agents():
    boss.reset()
    boss_aid.reset()
    coder.reset()
    pm.reset()
    reviewer.reset()


def rag_chat():
    _reset_agents()
    groupchat = autogen.GroupChat(
        agents=[boss_aid, pm, coder, reviewer], messages=[], max_round=12, speaker_selection_method="round_robin"
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss_aid as this is the user proxy agent.
    boss_aid.initiate_chat(
        manager,
        message=boss_aid.message_generator,
        problem=PROBLEM,
        n_results=3,
    )


def norag_chat():
    _reset_agents()
    groupchat = autogen.GroupChat(
        agents=[boss, pm, coder, reviewer],
        messages=[],
        max_round=12,
        speaker_selection_method="auto",
        allow_repeat_speaker=False,
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the boss as this is the user proxy agent.
    boss.initiate_chat(
        manager,
        message=PROBLEM,
    )


def call_rag_chat():
    _reset_agents()

    # In this case, we will have multiple user proxy agents and we don't initiate the chat
    # with RAG user proxy agent.
    # In order to use RAG user proxy agent, we need to wrap RAG agents in a function and call
    # it from other agents.
    def retrieve_content(
        message: Annotated[
            str,
            "Refined message which keeps the original meaning and can be used to retrieve content for code generation and question answering.",
        ],
        n_results: Annotated[int, "number of results"] = 3,
    ) -> str:
        boss_aid.n_results = n_results  # Set the number of results to be retrieved.
        # Check if we need to update the context.
        update_context_case1, update_context_case2 = boss_aid._check_update_context(message)
        if (update_context_case1 or update_context_case2) and boss_aid.update_context:
            boss_aid.problem = message if not hasattr(boss_aid, "problem") else boss_aid.problem
            _, ret_msg = boss_aid._generate_retrieve_user_reply(message)
        else:
            _context = {"problem": message, "n_results": n_results}
            ret_msg = boss_aid.message_generator(boss_aid, None, _context)
        return ret_msg if ret_msg else message

    boss_aid.human_input_mode = "NEVER"  # Disable human input for boss_aid since it only retrieves content.

    for caller in [pm, coder, reviewer]:
        d_retrieve_content = caller.register_for_llm(
            description="retrieve content for code generation and question answering.", api_style="function"
        )(retrieve_content)

    for executor in [boss, pm]:
        executor.register_for_execution()(d_retrieve_content)

    groupchat = autogen.GroupChat(
        agents=[boss, pm, coder, reviewer],
        messages=[],
        max_round=12,
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False,
    )

    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the boss as this is the user proxy agent.
    boss.initiate_chat(
        manager,
        message=PROBLEM,
    )


if __name__ == "__main__":
    # call_rag_chat()
    norag_chat()
    # rag_chat()