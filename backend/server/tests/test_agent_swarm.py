import pytest
import os
from unittest.mock import patch, MagicMock
from server.agent_swarm import run_swarm

@pytest.mark.asyncio
async def test_run_swarm_mocked():
    # Mock Gemini model responses to avoid network requests during local tests
    with patch("server.agent_swarm._GENAI_CLIENT") as mock_client:
        mock_models = MagicMock()
        mock_generate = MagicMock()
        
        # Define mock returns for each agent's call to Gemini
        # Agent 1 (triage): SEVERITY and ROUTING
        # Agent 2 (narrative): Formal narrative
        # Agent 3 (evidence): 5 items
        # Agent 4 (routing): specific next action
        # Agent 5 (empathy): warm message
        mock_generate.text = "SEVERITY: 0.8\nROUTING: AUTHORITY\n\nFormal Narrative of incident.\n1. Item 1\n2. Item 2\n3. Item 3\n4. Item 4\n5. Item 5\n\nVisit district office.\nReassuring message."
        mock_models.generate_content.return_value = mock_generate
        mock_client.models = mock_models

        # We also need to mock _get_genai_client to return our mock_client
        with patch("server.agent_swarm._get_genai_client", return_value=mock_client):
            res = await run_swarm(
                transcript="I was denied wage at the farm",
                incident_type="wage_theft",
                district="Belagavi",
                language="en"
            )
            assert res["severity"] == 0.8
            assert res["routing"] == "AUTHORITY"
            assert len(res["evidence_list"]) > 0
            assert res["pseudonym"].startswith("Citizen-")
