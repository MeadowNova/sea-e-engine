
#!/usr/bin/env python3
"""
Unit tests for workflow state management.
"""

import pytest
import tempfile
import time
import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from workflow.state import WorkflowStateManager, WorkflowStatus, WorkflowState, WorkflowStep


class TestWorkflowStateManager:
    """Test cases for WorkflowStateManager."""
    
    @pytest.fixture
    def temp_state_dir(self):
        """Create temporary state directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_manager_initialization(self, temp_state_dir):
        """Test state manager initialization."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        assert manager.state_dir == Path(temp_state_dir)
        assert isinstance(manager._state_cache, dict)
    
    def test_start_workflow(self, temp_state_dir):
        """Test starting a new workflow."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        input_data = {"design_name": "test_design", "product_type": "tshirt"}
        workflow_state = manager.start_workflow("test_workflow_1", input_data)
        
        assert workflow_state.workflow_id == "test_workflow_1"
        assert workflow_state.status == WorkflowStatus.RUNNING
        assert workflow_state.input_data == input_data
        assert workflow_state.start_time > 0
        assert workflow_state.end_time is None
    
    def test_start_duplicate_workflow(self, temp_state_dir):
        """Test starting a workflow with duplicate ID."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start first workflow
        manager.start_workflow("test_workflow_1", {})
        
        # Try to start duplicate
        with pytest.raises(ValueError) as exc_info:
            manager.start_workflow("test_workflow_1", {})
        
        assert "already running" in str(exc_info.value)
    
    def test_update_workflow_step(self, temp_state_dir):
        """Test updating workflow step."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflow
        manager.start_workflow("test_workflow_1", {})
        
        # Update step
        step_data = {"files": ["file1.png", "file2.png"]}
        workflow_state = manager.update_workflow_step("test_workflow_1", "generate_mockups", step_data)
        
        assert len(workflow_state.steps) == 1
        assert workflow_state.steps[0].step_name == "generate_mockups"
        assert workflow_state.steps[0].status == WorkflowStatus.COMPLETED
        assert workflow_state.steps[0].data == step_data
        assert workflow_state.steps[0].error_message is None
    
    def test_update_workflow_step_with_error(self, temp_state_dir):
        """Test updating workflow step with error."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflow
        manager.start_workflow("test_workflow_1", {})
        
        # Update step with error
        error_message = "Failed to generate mockups"
        workflow_state = manager.update_workflow_step("test_workflow_1", "generate_mockups", 
                                                     error_message=error_message)
        
        assert len(workflow_state.steps) == 1
        assert workflow_state.steps[0].status == WorkflowStatus.FAILED
        assert workflow_state.steps[0].error_message == error_message
    
    def test_complete_workflow(self, temp_state_dir):
        """Test completing a workflow."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflow
        manager.start_workflow("test_workflow_1", {})
        
        # Complete workflow
        output_data = {"product_id": "123", "listing_id": "456"}
        workflow_state = manager.complete_workflow("test_workflow_1", output_data)
        
        assert workflow_state.status == WorkflowStatus.COMPLETED
        assert workflow_state.output_data == output_data
        assert workflow_state.end_time > workflow_state.start_time
    
    def test_fail_workflow(self, temp_state_dir):
        """Test failing a workflow."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflow
        manager.start_workflow("test_workflow_1", {})
        
        # Fail workflow
        error_message = "Workflow failed due to API error"
        workflow_state = manager.fail_workflow("test_workflow_1", error_message)
        
        assert workflow_state.status == WorkflowStatus.FAILED
        assert workflow_state.error_message == error_message
        assert workflow_state.end_time > workflow_state.start_time
    
    def test_cancel_workflow(self, temp_state_dir):
        """Test cancelling a workflow."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflow
        manager.start_workflow("test_workflow_1", {})
        
        # Cancel workflow
        workflow_state = manager.cancel_workflow("test_workflow_1")
        
        assert workflow_state.status == WorkflowStatus.CANCELLED
        assert workflow_state.end_time > workflow_state.start_time
    
    def test_get_workflow_status(self, temp_state_dir):
        """Test getting workflow status."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflow
        original_state = manager.start_workflow("test_workflow_1", {})
        
        # Get status
        retrieved_state = manager.get_workflow_status("test_workflow_1")
        
        assert retrieved_state is not None
        assert retrieved_state.workflow_id == original_state.workflow_id
        assert retrieved_state.status == original_state.status
    
    def test_get_nonexistent_workflow_status(self, temp_state_dir):
        """Test getting status of nonexistent workflow."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        result = manager.get_workflow_status("nonexistent_workflow")
        
        assert result is None
    
    def test_list_workflows(self, temp_state_dir):
        """Test listing workflows."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start multiple workflows
        manager.start_workflow("workflow_1", {})
        manager.start_workflow("workflow_2", {})
        manager.complete_workflow("workflow_1", {})
        
        # List all workflows
        all_workflows = manager.list_workflows()
        assert len(all_workflows) == 2
        
        # List completed workflows
        completed_workflows = manager.list_workflows(WorkflowStatus.COMPLETED)
        assert len(completed_workflows) == 1
        assert completed_workflows[0].workflow_id == "workflow_1"
        
        # List running workflows
        running_workflows = manager.list_workflows(WorkflowStatus.RUNNING)
        assert len(running_workflows) == 1
        assert running_workflows[0].workflow_id == "workflow_2"
    
    def test_list_active_workflows(self, temp_state_dir):
        """Test listing active workflows."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Start workflows with different statuses
        manager.start_workflow("workflow_1", {})
        manager.start_workflow("workflow_2", {})
        manager.complete_workflow("workflow_1", {})
        
        active_workflows = manager.list_active_workflows()
        
        assert len(active_workflows) == 1
        assert "workflow_2" in active_workflows
    
    def test_state_persistence(self, temp_state_dir):
        """Test that workflow state persists across manager instances."""
        # Create first manager and start workflow
        manager1 = WorkflowStateManager(state_dir=temp_state_dir)
        manager1.start_workflow("persistent_workflow", {"test": "data"})
        manager1.update_workflow_step("persistent_workflow", "step1", {"result": "success"})
        
        # Create second manager (simulating restart)
        manager2 = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Check that workflow state was loaded
        workflow_state = manager2.get_workflow_status("persistent_workflow")
        
        assert workflow_state is not None
        assert workflow_state.workflow_id == "persistent_workflow"
        assert workflow_state.input_data == {"test": "data"}
        assert len(workflow_state.steps) == 1
        assert workflow_state.steps[0].step_name == "step1"
    
    def test_cleanup_old_workflows(self, temp_state_dir):
        """Test cleaning up old workflows."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Create old workflow by manipulating start time
        old_workflow = manager.start_workflow("old_workflow", {})
        old_workflow.start_time = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        manager.complete_workflow("old_workflow", {})
        
        # Create recent workflow
        manager.start_workflow("recent_workflow", {})
        
        # Manually update the old workflow's start time in cache and file
        manager._state_cache["old_workflow"].start_time = time.time() - (8 * 24 * 60 * 60)
        manager._save_state(manager._state_cache["old_workflow"])
        
        # Clean up workflows older than 7 days
        manager.cleanup_old_workflows(days=7)
        
        # Check that old workflow was removed and recent one remains
        assert manager.get_workflow_status("old_workflow") is None
        assert manager.get_workflow_status("recent_workflow") is not None
    
    def test_get_workflow_statistics(self, temp_state_dir):
        """Test getting workflow statistics."""
        manager = WorkflowStateManager(state_dir=temp_state_dir)
        
        # Create workflows with different statuses
        manager.start_workflow("workflow_1", {})
        manager.start_workflow("workflow_2", {})
        manager.complete_workflow("workflow_1", {})
        manager.fail_workflow("workflow_2", "Test error")
        
        stats = manager.get_workflow_statistics()
        
        assert stats["total_workflows"] == 2
        assert stats["status_counts"]["completed"] == 1
        assert stats["status_counts"]["failed"] == 1
        assert stats["active_workflows"] == 0


class TestWorkflowStep:
    """Test cases for WorkflowStep dataclass."""
    
    def test_workflow_step_creation(self):
        """Test WorkflowStep creation."""
        step = WorkflowStep(
            step_name="test_step",
            status=WorkflowStatus.COMPLETED,
            start_time=time.time(),
            end_time=time.time() + 10,
            data={"result": "success"},
            error_message=None
        )
        
        assert step.step_name == "test_step"
        assert step.status == WorkflowStatus.COMPLETED
        assert step.data == {"result": "success"}
        assert step.error_message is None


class TestWorkflowState:
    """Test cases for WorkflowState dataclass."""
    
    def test_workflow_state_creation(self):
        """Test WorkflowState creation."""
        state = WorkflowState(
            workflow_id="test_workflow",
            status=WorkflowStatus.RUNNING,
            start_time=time.time(),
            input_data={"test": "data"}
        )
        
        assert state.workflow_id == "test_workflow"
        assert state.status == WorkflowStatus.RUNNING
        assert state.input_data == {"test": "data"}
        assert state.steps == []  # Should be initialized as empty list
    
    def test_workflow_state_with_steps(self):
        """Test WorkflowState with steps."""
        step1 = WorkflowStep("step1", WorkflowStatus.COMPLETED, time.time())
        step2 = WorkflowStep("step2", WorkflowStatus.RUNNING, time.time())
        
        state = WorkflowState(
            workflow_id="test_workflow",
            status=WorkflowStatus.RUNNING,
            start_time=time.time(),
            steps=[step1, step2]
        )
        
        assert len(state.steps) == 2
        assert state.steps[0].step_name == "step1"
        assert state.steps[1].step_name == "step2"


if __name__ == "__main__":
    pytest.main([__file__])
