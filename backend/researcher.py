from tavily import TavilyClient
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class Researcher:
    def __init__(
        self, 
        interests, 
        debug=True, 
        podcast="", 
        verbose=False, 
        nsubjects=5,
        subject = ''
    ):
        self.debug = debug
        self.interests = interests
        self.podcast = podcast
        self.verbose = verbose
        self.subject = subject
        self.nsubjects = nsubjects
        load_dotenv(dotenv_path="backend/env/tavily.env") 
        load_dotenv(dotenv_path="backend/env/openai.env")
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.llm = ChatOpenAI(model="gpt-4o")
        if debug:
            self.client = None
            self.llm = None
            

    def subjects(self):
        load_dotenv(dotenv_path="env/openai.env")
        self.llm = ChatOpenAI(model="gpt-4o")
        if self.debug:
            self.llm = None
        prompt = f"Based on this news about {", ".join(self.interests)}, give me {self.nsubjects} short, engaging podcast episodes titles/subjects. The podcast is {self.podcast}. "
        prompt += "Don't use any formatting tricks. Simply put each subject as a sentence, followed by '/'. "
        prompt += "For example: 'Beyond the Frame: Exploring DEI in Europe's Growing Cinema Scene/Barks and Bites: The Canine & Culinary Culture of Europe/Artful Escapes: Traveling through Europe's Hidden Creative Hubs'"
        if not self.debug:
            result = self.llm.invoke(prompt).content
        else:
            result = "Savor the Screen: How Cinema Shapes Europe's Culinary Trends/Paws and Performance: The Role of Dogs in Europe's Sports Scene/Journey with a Purpose: How DEI is Transforming Travel Across Europe"
        result = result.split(sep='/')
        print(r for r in result if self.verbose)
        return result
    

    def fetch_context(self):
        if self.debug:
            return "- AI tools are being used by amateur filmmakers in Europe to generate cinematography.\n- Dogs are increasingly featured in sports sponsorship campaigns."
        query = f"latest trending news and interesting developments related to: {self.subject}"
        search_result = self.client.search(query=query, search_depth="basic", max_results=len(self.interests))
        context = "\n".join([f"- {r['title']}: {r['content']}" for r in search_result['results']])
        if self.verbose:
            print("Context:", context)
        return context
        

