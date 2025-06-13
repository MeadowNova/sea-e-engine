
#!/usr/bin/env python3
"""
Workflow State Manager for SEA-E Engine
=======================================

Manages workflow state, progress tracking, and recovery mechanisms
for the SEA-E automation engine.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Individual workflow step data."""
    step_name: str
    status: WorkflowStatus
    start_time: float
    end_time: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowState:
    """Complete workflow state data."""
    workflow_id: str
    status: WorkflowStatus
    start_time: float
    end_time: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    steps: List[WorkflowStep] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []


class WorkflowStateManager:
    """
    Manages workflow state persistence and recovery for the SEA-E engine.
    
    This class provides state management capabilities including:
    - Workflow state persistence
    - Progress tracking
    - Error recovery
    - State cleanup
    """
    
    def __init__(self, state_dir: str = "logs/workflows"):
        """
        Initialize workflow state manager.
        
        Args:
            state_dir: Directory to store workflow state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("workflow_state")
        
        # In-memory state cache
        self._state_cache: Dict[str, WorkflowState] = {}
        
        # Load existing states
        self._load_existing_states()
    
    def _load_existing_states(self):
        """Load existing workflow states from disk."""
        try:
            self.logger.info("Loading existing workflow states...")
            
            state_files = list(self.state_dir.glob("*.json"))
            loaded_count = 0
            
            for state_file in state_files:
                try:
                    with open(state_file, 'r') as f:
                        state_data = json.load(f)
                    
                    # Convert to WorkflowState object
                    workflow_state = self._dict_to_workflow_state(state_data)
                    self._state_cache[workflow_state.workflow_id] = workflow_state
                    loaded_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to load state file {state_file}: {e}")
                    continue
            
            self.logger.info(f"Loaded {loaded_count} existing workflow states")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing states: {e}")
    
    def _dict_to_workflow_state(self, data: Dict[str, Any]) -> WorkflowState:
        """Convert dictionary to WorkflowState object."""
        # Convert steps
        steps = []
        for step_data in data.get("steps", []):
            step = WorkflowStep(
                step_name=step_data["step_name"],
                status=WorkflowStatus(step_data["status"]),
                start_time=step_data["start_time"],
                end_time=step_data.get("end_time"),
                data=step_data.get("data"),
                error_message=step_data.get("error_message")
            )
            steps.append(step)
        
        # Create workflow state
        workflow_state = WorkflowState(
            workflow_id=data["workflow_id"],
            status=WorkflowStatus(data["status"]),
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            input_data=data.get("input_data"),
            output_data=data.get("output_data"),
            steps=steps,
            error_message=data.get("error_message")
        )
        
        return workflow_state
    
    def _workflow_state_to_dict(self, state: WorkflowState) -> Dict[str, Any]:
        """Convert WorkflowState object to dictionary."""
        data = asdict(state)
        
        # Convert enum values to strings
        data["status"] = state.status.value
        
        for step_data in data["steps"]:
            step_data["status"] = step_data["status"].value
        
        return data
    
    def _save_state(self, workflow_state: WorkflowState):
        """Save workflow state to disk."""
        try:
            state_file = self.state_dir / f"{workflow_state.workflow_id}.json"
            
            # Convert to dictionary
            state_data = self._workflow_state_to_dict(workflow_state)
            
            # Save to file
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            # Update cache
            self._state_cache[workflow_state.workflow_id] = workflow_state
            
        except Exception as e:
            self.logger.error(f"Failed to save workflow state {workflow_state.workflow_id}: {e}")
            raise
    
    def start_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> WorkflowState:
        """
        Start a new workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            input_data: Initial workflow input data
            
        Returns:
            WorkflowState: Created workflow state
        """
        try:
            self.logger.info(f"Starting workflow: {workflow_id}")
            
            # Check if workflow already exists
            if workflow_id in self._state_cache:
                existing_state = self._state_cache[workflow_id]
                if existing_state.status in [WorkflowStatus.RUNNING, WorkflowStatus.PENDING]:
                    raise ValueError(f"Workflow {workflow_id} is already running")
            
            # Create new workflow state
            workflow_state = WorkflowState(
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING,
                start_time=time.time(),
                input_data=input_data or {}
            )
            
            # Save state
            self._save_state(workflow_state)
            
            self.logger.info(f"Workflow {workflow_id} started successfully")
            return workflow_state
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow {workflow_id}: {e}")
            raise
    
    def update_workflow_step(self, workflow_id: str, step_name: str, 
                           step_data: Dict[str, Any] = None, 
                           error_message: str = None) -> WorkflowState:
        """
        Update or add a workflow step.
        
        Args:
            workflow_id: Workflow identifier
            step_name: Name of the step
            step_data: Step output data
            error_message: Error message if step failed
            
        Returns:
            WorkflowState: Updated workflow state
        """
        try:
            self.logger.info(f"Updating workflow step: {workflow_id} - {step_name}")
            
            # Get current workflow state
            if workflow_id not in self._state_cache:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow_state = self._state_cache[workflow_id]
            
            # Find existing step or create new one
            existing_step = None
            for step in workflow_state.steps:
                if step.step_name == step_name:
                    existing_step = step
                    break
            
            if existing_step:
                # Update existing step
                existing_step.end_time = time.time()
                existing_step.data = step_data
                existing_step.error_message = error_message
                existing_step.status = WorkflowStatus.FAILED if error_message else WorkflowStatus.COMPLETED
            else:
                # Create new step
                new_step = WorkflowStep(
                    step_name=step_name,
                    status=WorkflowStatus.FAILED if error_message else WorkflowStatus.COMPLETED,
                    start_time=time.time(),
                    end_time=time.time(),
                    data=step_data,
                    error_message=error_message
                )
                workflow_state.steps.append(new_step)
            
            # Save updated state
            self._save_state(workflow_state)
            
            self.logger.info(f"Workflow step updated: {step_name}")
            return workflow_state
            
        except Exception as e:
            self.logger.error(f"Failed to update workflow step {workflow_id} - {step_name}: {e}")
            raise
    
    def complete_workflow(self, workflow_id: str, output_data: Dict[str, Any] = None) -> WorkflowState:
        """
        Mark workflow as completed.
        
        Args:
            workflow_id: Workflow identifier
            output_data: Final workflow output data
            
        Returns:
            WorkflowState: Completed workflow state
        """
        try:
            self.logger.info(f"Completing workflow: {workflow_id}")
            
            # Get current workflow state
            if workflow_id not in self._state_cache:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow_state = self._state_cache[workflow_id]
            
            # Update workflow state
            workflow_state.status = WorkflowStatus.COMPLETED
            workflow_state.end_time = time.time()
            workflow_state.output_data = output_data or {}
            
            # Save updated state
            self._save_state(workflow_state)
            
            execution_time = workflow_state.end_time - workflow_state.start_time
            self.logger.info(f"Workflow {workflow_id} completed in {execution_time:.2f} seconds")
            
            return workflow_state
            
        except Exception as e:
            self.logger.error(f"Failed to complete workflow {workflow_id}: {e}")
            raise
    
    def fail_workflow(self, workflow_id: str, error_message: str) -> WorkflowState:
        """
        Mark workflow as failed.
        
        Args:
            workflow_id: Workflow identifier
            error_message: Error message describing the failure
            
        Returns:
            WorkflowState: Failed workflow state
        """
        try:
            self.logger.info(f"Failing workflow: {workflow_id}")
            
            # Get current workflow state
            if workflow_id not in self._state_cache:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow_state = self._state_cache[workflow_id]
            
            # Update workflow state
            workflow_state.status = WorkflowStatus.FAILED
            workflow_state.end_time = time.time()
            workflow_state.error_message = error_message
            
            # Save updated state
            self._save_state(workflow_state)
            
            self.logger.info(f"Workflow {workflow_id} marked as failed: {error_message}")
            return workflow_state
            
        except Exception as e:
            self.logger.error(f"Failed to fail workflow {workflow_id}: {e}")
            raise
    
    def cancel_workflow(self, workflow_id: str) -> WorkflowState:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            WorkflowState: Cancelled workflow state
        """
        try:
            self.logger.info(f"Cancelling workflow: {workflow_id}")
            
            # Get current workflow state
            if workflow_id not in self._state_cache:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow_state = self._state_cache[workflow_id]
            
            # Update workflow state
            workflow_state.status = WorkflowStatus.CANCELLED
            workflow_state.end_time = time.time()
            
            # Save updated state
            self._save_state(workflow_state)
            
            self.logger.info(f"Workflow {workflow_id} cancelled")
            return workflow_state
            
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow {workflow_id}: {e}")
            raise
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Get current workflow status.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            WorkflowState: Current workflow state or None if not found
        """
        return self._state_cache.get(workflow_id)
    
    def list_workflows(self, status: WorkflowStatus = None) -> List[WorkflowState]:
        """
        List workflows, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List[WorkflowState]: List of workflow states
        """
        workflows = list(self._state_cache.values())
        
        if status:
            workflows = [w for w in workflows if w.status == status]
        
        # Sort by start time (newest first)
        workflows.sort(key=lambda w: w.start_time, reverse=True)
        
        return workflows
    
    def list_active_workflows(self) -> List[str]:
        """
        List IDs of active (running or pending) workflows.
        
        Returns:
            List[str]: List of active workflow IDs
        """
        active_statuses = [WorkflowStatus.RUNNING, WorkflowStatus.PENDING]
        active_workflows = [
            w.workflow_id for w in self._state_cache.values()
            if w.status in active_statuses
        ]
        
        return active_workflows
    
    def cleanup_old_workflows(self, days: int = 7):
        """
        Clean up workflow states older than specified days.
        
        Args:
            days: Number of days to keep workflows
        """
        try:
            self.logger.info(f"Cleaning up workflows older than {days} days...")
            
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            cleaned_count = 0
            
            # Find old workflows
            workflows_to_remove = []
            for workflow_id, workflow_state in self._state_cache.items():
                if workflow_state.start_time < cutoff_time:
                    # Only clean up completed, failed, or cancelled workflows
                    if workflow_state.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                        workflows_to_remove.append(workflow_id)
            
            # Remove old workflows
            for workflow_id in workflows_to_remove:
                try:
                    # Remove from cache
                    del self._state_cache[workflow_id]
                    
                    # Remove state file
                    state_file = self.state_dir / f"{workflow_id}.json"
                    if state_file.exists():
                        state_file.unlink()
                    
                    cleaned_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to clean up workflow {workflow_id}: {e}")
                    continue
            
            self.logger.info(f"Cleaned up {cleaned_count} old workflows")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old workflows: {e}")
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        Get workflow statistics.
        
        Returns:
            Dict[str, Any]: Workflow statistics
        """
        try:
            workflows = list(self._state_cache.values())
            
            # Count by status
            status_counts = {}
            for status in WorkflowStatus:
                status_counts[status.value] = sum(1 for w in workflows if w.status == status)
            
            # Calculate execution times for completed workflows
            completed_workflows = [w for w in workflows if w.status == WorkflowStatus.COMPLETED and w.end_time]
            execution_times = [w.end_time - w.start_time for w in completed_workflows]
            
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Recent activity (last 24 hours)
            recent_cutoff = time.time() - (24 * 60 * 60)
            recent_workflows = [w for w in workflows if w.start_time > recent_cutoff]
            
            statistics = {
                "total_workflows": len(workflows),
                "status_counts": status_counts,
                "average_execution_time": avg_execution_time,
                "recent_workflows_24h": len(recent_workflows),
                "active_workflows": len(self.list_active_workflows())
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow statistics: {e}")
            return {}
