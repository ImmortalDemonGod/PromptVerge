#!/usr/bin/env python3
"""Test the full knowledge workflow including quiz generation."""

from pathlib import Path
from promptverge.flows.knowledge_workflow import run_knowledge_flow

def test_full_workflow(tmp_path):
    """Test the complete knowledge workflow."""
    
    # Read the dummy paper
    paper_path = Path(__file__).parent / "fixtures/dummy_paper.txt"
    with open(paper_path, 'r') as f:
        paper_content = f.read()
    
    print("📜 Testing full knowledge workflow...")
    print(f"Input: '{paper_content[:100]}...'")
    print()
    
    try:
        print("🤖 Running knowledge workflow...")
        quiz = run_knowledge_flow(paper_content)
        
        print("✅ Workflow completed!")
        print("📋 Generated quiz:")
        print(f"  Title: {quiz.title}")
        print(f"  Questions: {len(quiz.questions)}")
        print(f"  Status: {quiz.status}")
        print(f"  Tags: {quiz.tags}")
        
        if quiz.questions:
            print("\n❓ Sample questions:")
            for i, q in enumerate(quiz.questions[:2], 1):
                print(f"  {i}. {q.q}")
                print(f"     Answer: {q.correct_answer}")
        
        # Save results
        output_path = tmp_path / "full_workflow_results.txt"
        with open(output_path, 'w') as f:
            f.write(f"Title: {quiz.title}\n")
            f.write(f"Questions: {len(quiz.questions)}\n")
            f.write(f"Status: {quiz.status}\n")
            f.write(f"Tags: {quiz.tags}\n")
            if quiz.questions:
                f.write("\nQuestions:\n")
                for i, q in enumerate(quiz.questions, 1):
                    f.write(f"{i}. {q.q}\n")
                    f.write(f"   Answer: {q.correct_answer}\n")
        
        print(f"\n💾 Results saved to {output_path}")
        assert quiz is not None
        assert quiz.questions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Workflow failed with exception: {e}"

if __name__ == "__main__":
    test_full_workflow()
