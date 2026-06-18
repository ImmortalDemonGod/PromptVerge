#!/usr/bin/env python3
"""Direct test of KG extraction functionality."""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from promptverge.flows.knowledge_workflow import extract_kg_triples

def test_kg_extraction():
    """Test the KG extraction with real scientific text."""

    output_lines = []

    # Read the dummy paper
    paper_path = Path(__file__).parent / "fixtures" / "dummy_paper.txt"
    with open(paper_path, 'r') as f:
        paper_content = f.read()

    msg = "📜 Input text:"
    print(msg)
    output_lines.append(msg)

    msg = f"'{paper_content[:100]}...'"
    print(msg)
    output_lines.append(msg)
    output_lines.append("")

    msg = "🔍 Extracting knowledge graph triples..."
    print(msg)
    output_lines.append(msg)

    try:
        triples = extract_kg_triples(paper_content)

        msg = "✅ Extraction completed!"
        print(msg)
        output_lines.append(msg)

        msg = f"📊 Found {len(triples)} triples:"
        print(msg)
        output_lines.append(msg)

        if triples:
            for i, (head, relation, tail) in enumerate(triples, 1):
                msg = f"  {i}. ({head}, {relation}, {tail})"
                print(msg)
                output_lines.append(msg)
        else:
            msg = "  (No triples extracted)"
            print(msg)
            output_lines.append(msg)

        # Save output to file
        with open('kg_extraction_results.txt', 'w') as f:
            f.write('\n'.join(output_lines))

        print("\n💾 Results saved to kg_extraction_results.txt")
        assert triples is not None, "The extraction should return a list of triples, not None."
        assert isinstance(triples, list), f"Expected a list of triples, but got {type(triples)}."

    except Exception as e:
        msg = f"❌ Error during extraction: {e}"
        print(msg)
        output_lines.append(msg)

        import traceback
        error_trace = traceback.format_exc()
        print(error_trace)
        output_lines.append(error_trace)

        # Save error output to file
        with open('kg_extraction_results.txt', 'w') as f:
            f.write('\n'.join(output_lines))

        assert False, f"Error during extraction: {e}"

if __name__ == "__main__":
    test_kg_extraction()
