"""
Simplified runner script for the raw material sourcing workflow
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow_orchestrator import RawMaterialSourcingWorkflow

async def run_demo():
    """Run a demo of the workflow with predefined inputs"""
    print("🚀 Raw Material Sourcing Workflow Demo")
    print("=" * 50)
    
    # Demo inputs
    raw_materials = ["chocolate", "coffee", "cotton"]
    
    for material in raw_materials:
        print(f"\n📦 Analyzing: {material}")
        print("-" * 30)
        
        workflow = RawMaterialSourcingWorkflow()
        
        try:
            results = await workflow.execute_workflow(
                raw_material=material,
                destination_country="USA"
            )
            
            # Display summary
            final_rec = results["final_recommendation"]
            print(f"✅ Best Source: {final_rec['recommended_source_country']}")
            print(f"📊 Overall Rating: {final_rec['overall_rating']}")
            print(f"🏆 Composite Score: {final_rec['composite_score']:.2f}/10")
            
        except Exception as e:
            print(f"❌ Error analyzing {material}: {str(e)}")
        
        print("-" * 50)

async def run_interactive():
    """Run interactive workflow"""
    workflow = RawMaterialSourcingWorkflow()
    
    print("🌟 Interactive Raw Material Sourcing Analysis")
    print("=" * 50)
    
    raw_material = input("Enter raw material: ").strip()
    if not raw_material:
        print("❌ Raw material is required")
        return
    
    destination = input("Enter destination country (default: USA): ").strip()
    if not destination:
        destination = "USA"
    
    try:
        results = await workflow.execute_workflow(raw_material, destination)
        
        # Save detailed results
        import json
        filename = f"analysis_{raw_material.replace(' ', '_')}_{destination.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    print("Raw Material Sourcing Workflow")
    print("1. Run Demo (analyze chocolate, coffee, cotton)")
    print("2. Interactive Mode")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(run_demo())
    elif choice == "2":
        asyncio.run(run_interactive())
    else:
        print("Invalid choice. Running demo by default.")
        asyncio.run(run_demo())

if __name__ == "__main__":
    main()