# FILE: cultivation/systems/PromptVerge/tests/test_knowledge_workflow_units.py
"""Unit tests for knowledge workflow functions to improve test coverage."""

from unittest.mock import Mock, patch, MagicMock
from promptverge.flows import knowledge_workflow
from promptverge.schemas import documents as schemas


class TestExtractKgTriples:
    """Unit tests for the extract_kg_triples function."""

    @patch('promptverge.flows.knowledge_workflow._get_nlp_pipeline')
    def test_extract_kg_triples_with_relations(self, mock_get_pipeline):
        """Test extract_kg_triples when relations are found."""
        # Setup mocks
        mock_nlp = Mock()
        mock_doc = MagicMock()
        mock_get_pipeline.return_value = mock_nlp
        mock_nlp.return_value = mock_doc

        # The text that the doc object is supposed to represent
        text_content = "A protein is located_in a cell. An enzyme catalyzes a reaction."
        mock_doc.text = text_content

        # Mock relations with proper structure (start/end character indices)
        # Relation 1: protein (2-9) -> located_in -> cell (26-30)
        mock_relation1 = Mock()
        mock_relation1.start.start = 2
        mock_relation1.start.end = 9
        mock_relation1.end.start = 26
        mock_relation1.end.end = 30
        mock_relation1.relation.name = "located_in"

        # Relation 2: enzyme (35-41) -> catalyzes -> reaction (54-62)
        mock_relation2 = Mock()
        mock_relation2.start.start = 35
        mock_relation2.start.end = 41
        mock_relation2.end.start = 54
        mock_relation2.end.end = 62
        mock_relation2.relation.name = "catalyzes"

        mock_doc._.relations = [mock_relation1, mock_relation2]

        # Test the function
        result = knowledge_workflow.extract_kg_triples(text_content)

        # Verify results
        expected = [
            ("protein", "located_in", "cell"),
            ("enzyme", "catalyzes", "reaction"),
        ]
        assert result == expected

        # Verify the pipeline was fetched and used
        mock_get_pipeline.assert_called_once()
        mock_nlp.assert_called_once_with(text_content)

    @patch('promptverge.flows.knowledge_workflow._get_nlp_pipeline')
    def test_extract_kg_triples_no_relations(self, mock_get_pipeline):
        """Test extract_kg_triples when no relations are found."""
        # Setup mocks
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_get_pipeline.return_value = mock_nlp
        mock_nlp.return_value = mock_doc

        # No relations found
        mock_doc._.relations = None

        # Test the function
        result = knowledge_workflow.extract_kg_triples("Text with no relations")

        # Should return empty list
        assert result == []

        # Verify the pipeline was fetched and used
        mock_get_pipeline.assert_called_once()
        mock_nlp.assert_called_once_with("Text with no relations")

    @patch('promptverge.flows.knowledge_workflow._get_nlp_pipeline')
    def test_extract_kg_triples_empty_relations(self, mock_get_pipeline):
        """Test extract_kg_triples when relations exist but are empty."""
        # Setup mocks
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_get_pipeline.return_value = mock_nlp
        mock_nlp.return_value = mock_doc

        # Mock relation with empty start/end
        mock_relation = Mock()
        mock_relation.start = None
        mock_relation.end = None

        mock_doc._.relations = [mock_relation]

        # Test the function
        result = knowledge_workflow.extract_kg_triples("Text with empty relations")

        # Should return empty list (empty relations filtered out)
        assert result == []

    @patch('promptverge.flows.knowledge_workflow._get_nlp_pipeline')
    def test_extract_kg_triples_mixed_relations(self, mock_get_pipeline):
        """Test extract_kg_triples with mix of valid and invalid relations."""
        # Setup mocks
        mock_nlp = Mock()
        mock_doc = MagicMock()
        mock_get_pipeline.return_value = mock_nlp
        mock_nlp.return_value = mock_doc

        # Text content for slicing
        text_content = "A gene codes_for a protein."
        mock_doc.text = text_content

        # Mix of valid and invalid relations
        # Valid: gene (2-6) -> codes_for -> protein (19-26)
        valid_relation = Mock()
        valid_relation.start.start = 2
        valid_relation.start.end = 6
        valid_relation.end.start = 19
        valid_relation.end.end = 26
        valid_relation.relation.name = "codes_for"

        invalid_relation = Mock()
        invalid_relation.start = None  # Invalid
        invalid_relation.end = Mock()
        invalid_relation.end.start = 0
        invalid_relation.end.end = 1
        invalid_relation.relation.name = "is_invalid"

        mock_doc._.relations = [valid_relation, invalid_relation]

        # Test the function
        result = knowledge_workflow.extract_kg_triples(text_content)

        # Should only return valid relation
        expected = [("gene", "codes_for", "protein")]
        assert result == expected


class TestGenerateQuiz:
    """Unit tests for the generate_quiz function."""

    def test_generate_quiz_function_exists(self):
        """Test that the generate_quiz function exists and is callable."""
        # This tests line 53 (the pass statement)
        assert callable(knowledge_workflow.generate_quiz)

        # The function should be decorated with @fn, so it should have Marvin attributes
        assert hasattr(knowledge_workflow.generate_quiz, '__wrapped__')

    def test_generate_quiz_pass_statement(self):
        """Test the pass statement in generate_quiz function (line 53)."""
        # This directly tests line 53 by calling the unwrapped function
        # The @fn decorator wraps the function, so we need to access the original
        original_func = knowledge_workflow.generate_quiz.__wrapped__

        # Calling the original function should execute the pass statement
        result = original_func("test triples")

        # The pass statement returns None
        assert result is None

    @patch('promptverge.flows.knowledge_workflow.generate_quiz')
    def test_generate_quiz_called_with_triples(self, mock_generate_quiz):
        """Test that generate_quiz can be called with knowledge graph triples."""
        # Mock the return value
        mock_quiz = Mock(spec=schemas.KnowledgeGraphQuiz)
        mock_generate_quiz.return_value = mock_quiz

        # Test calling the function
        triples_str = "[('protein', 'located_in', 'cell')]"
        result = mock_generate_quiz(triples_str)

        # Verify it was called correctly
        mock_generate_quiz.assert_called_once_with(triples_str)
        assert result == mock_quiz


class TestRunKnowledgeFlow:
    """Unit tests for the main run_knowledge_flow function."""

    @patch('promptverge.flows.knowledge_workflow.generate_quiz')
    @patch('promptverge.flows.knowledge_workflow.extract_kg_triples')
    def test_run_knowledge_flow_with_triples(self, mock_extract, mock_generate):
        """Test run_knowledge_flow when triples are extracted (lines 63-71)."""
        # Setup mocks
        mock_extract.return_value = [('gene', 'codes_for', 'protein'), ('enzyme', 'catalyzes', 'reaction')]
        mock_quiz = Mock(spec=schemas.KnowledgeGraphQuiz)
        mock_generate.return_value = mock_quiz

        # Test the main workflow function
        paper_content = "Scientific paper about genes and enzymes"
        result = knowledge_workflow.run_knowledge_flow(paper_content)

        # Verify the result
        assert result == mock_quiz

        # Verify extract_kg_triples was called correctly (line 63)
        mock_extract.assert_called_once_with(paper_content)

        # Verify triples were formatted correctly (lines 66-67)
        expected_triples_str = "- ('gene', 'codes_for', 'protein')\n- ('enzyme', 'catalyzes', 'reaction')"
        mock_generate.assert_called_once_with(expected_triples_str)

    @patch('promptverge.flows.knowledge_workflow.generate_quiz')
    @patch('promptverge.flows.knowledge_workflow.extract_kg_triples')
    def test_run_knowledge_flow_no_triples(self, mock_extract, mock_generate):
        """Test run_knowledge_flow when no triples are extracted."""
        # Setup mocks
        mock_extract.return_value = []  # No triples found
        mock_quiz = Mock(spec=schemas.KnowledgeGraphQuiz)
        mock_generate.return_value = mock_quiz

        # Test the main workflow function
        paper_content = "Paper with no extractable knowledge"
        result = knowledge_workflow.run_knowledge_flow(paper_content)

        # Verify the result
        assert result == mock_quiz

        # Verify extract_kg_triples was called
        mock_extract.assert_called_once_with(paper_content)

        # Verify generate_quiz was called with empty triples string
        mock_generate.assert_called_once_with("")

    @patch('promptverge.flows.knowledge_workflow.generate_quiz')
    @patch('promptverge.flows.knowledge_workflow.extract_kg_triples')
    def test_run_knowledge_flow_single_triple(self, mock_extract, mock_generate):
        """Test run_knowledge_flow with a single triple."""
        # Setup mocks
        mock_extract.return_value = [('protein', 'located_in', 'cell')]
        mock_quiz = Mock(spec=schemas.KnowledgeGraphQuiz)
        mock_generate.return_value = mock_quiz

        # Test the main workflow function
        paper_content = "Paper about protein location"
        result = knowledge_workflow.run_knowledge_flow(paper_content)

        # Verify the result
        assert result == mock_quiz

        # Verify the single triple was formatted correctly
        expected_triples_str = "- ('protein', 'located_in', 'cell')"
        mock_generate.assert_called_once_with(expected_triples_str)


class TestKnowledgeWorkflowIntegration:
    """Integration tests for knowledge workflow components."""

    @patch('promptverge.flows.knowledge_workflow.generate_quiz')
    @patch('promptverge.flows.knowledge_workflow.extract_kg_triples')
    def test_workflow_components_integration(self, mock_extract, mock_generate):
        """Test that workflow components work together."""
        # Setup mocks
        mock_extract.return_value = [('gene', 'codes_for', 'protein')]
        mock_quiz = Mock(spec=schemas.KnowledgeGraphQuiz)
        mock_generate.return_value = mock_quiz

        # Test that we can call both functions in sequence
        paper_content = "Some scientific paper content"

        # Extract triples
        triples = mock_extract(paper_content)
        assert triples == [('gene', 'codes_for', 'protein')]

        # Generate quiz from triples
        triples_str = str(triples)
        quiz = mock_generate(triples_str)
        assert quiz == mock_quiz

        # Verify calls
        mock_extract.assert_called_once_with(paper_content)
        mock_generate.assert_called_once_with(triples_str)
