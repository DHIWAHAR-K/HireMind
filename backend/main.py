import os
import asyncio
from dotenv import load_dotenv
from src.workflows import HiringWorkflow
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str, content: str):
    """Pretty print a section."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")
    print(content)
    print(f"{'='*60}\n")


async def run_hiring_workflow():
    """Run the complete hiring workflow."""
    print("\n🚀 Welcome to HireMind - AI-Powered Hiring Assistant")
    print("="*60)
    
    # Get user input
    print("\nLet's plan your hiring process!")
    print("\nPlease describe the role you want to hire for:")
    print("(Include details like: title, department, key skills, experience level)")
    
    user_input = input("\n> ")
    
    if not user_input.strip():
        print("❌ No input provided. Exiting...")
        return
    
    print("\n⏳ Processing your request...")
    
    # Initialize workflow
    workflow = HiringWorkflow()
    
    try:
        # Run the workflow
        result = await workflow.arun(user_input)
        
        if result["success"]:
            print("\n✅ Hiring process plan completed successfully!")
            
            # Display results
            if result.get("role_definition"):
                print_section("📋 Role Definition", 
                            result["role_definition"]["output"])
            
            if result.get("job_description"):
                print_section("📄 Job Description", 
                            result["job_description"])
            
            if result.get("interview_plan"):
                print_section("🎯 Interview Plan", 
                            result["interview_plan"]["output"])
            
            if result.get("timeline"):
                print_section("📅 Timeline Estimation", 
                            result["timeline"]["output"])
            
            if result.get("salary_benchmark"):
                print_section("💰 Salary Benchmark", 
                            result["salary_benchmark"]["output"])
            
            if result.get("offer_letter"):
                print_section("✉️ Offer Letter Template", 
                            result["offer_letter"])
            
            # Summary
            print("\n📊 Summary:")
            print(f"Completed stages: {', '.join(result['completed_stages'])}")
            
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error occurred')}")
            
    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        print(f"\n❌ An error occurred: {str(e)}")


def run_interactive_mode():
    """Run in interactive mode with individual agents."""
    from src.agents import RoleDefinitionAgent, JDGeneratorAgent, InterviewPlannerAgent
    from src.tools import get_all_tools
    
    print("\n🤖 Interactive Mode - Work with Individual Agents")
    print("="*60)
    
    tools = get_all_tools()
    agents = {
        "1": ("Role Definition", RoleDefinitionAgent(tools)),
        "2": ("JD Generator", JDGeneratorAgent(tools)),
        "3": ("Interview Planner", InterviewPlannerAgent(tools)),
    }
    
    while True:
        print("\nAvailable Agents:")
        for key, (name, _) in agents.items():
            print(f"{key}. {name}")
        print("4. Run Complete Workflow")
        print("5. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == "5":
            print("\n👋 Thank you for using HireMind!")
            break
        elif choice == "4":
            asyncio.run(run_hiring_workflow())
        elif choice in agents:
            name, agent = agents[choice]
            print(f"\n🤖 {name} Agent")
            print("-"*40)
            
            user_input = input("Enter your request: ")
            if user_input.strip():
                print("\n⏳ Processing...")
                result = agent.run(user_input)
                
                if result["success"]:
                    print_section(f"{name} Result", result["output"])
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Invalid option. Please try again.")


def main():
    """Main entry point."""
    print("\n🎯 HireMind - AI-Powered Hiring Assistant")
    print("="*60)
    print("\nHow would you like to use HireMind?")
    print("1. Run Complete Hiring Workflow (Recommended)")
    print("2. Interactive Mode (Work with Individual Agents)")
    print("3. Exit")
    
    choice = input("\nSelect an option: ")
    
    if choice == "1":
        asyncio.run(run_hiring_workflow())
    elif choice == "2":
        run_interactive_mode()
    elif choice == "3":
        print("\n👋 Goodbye!")
    else:
        print("❌ Invalid option. Please run the program again.")


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file or environment.")
        print("\nExample: export OPENAI_API_KEY='your-api-key-here'")
    else:
        main()