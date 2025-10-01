from typing import List

from fastapi import FastAPI, HTTPException
import logging

from core.model.WaveNode import WaveNode
from core.storage.WavesLabRepository import repository
from server.web_api.NodeUpdate import NodeUpdate

logger = logging.getLogger(__name__)


class WaveLabAPI:
    """WavesLab API application wrapper."""

    def __init__(self):
        """
        Initialize the WavesLab API application.
        """
        self.repo = repository
        self.app = FastAPI(
            title="WavesLab API",
            description="REST API for WavesLab household simulation environment",
            version="1.0.0"
        )
        self._setup_routes()

    def _setup_routes(self):
        """Set up all API routes."""

        @self.app.get("/", summary="Root endpoint")
        async def root():
            """Root endpoint with basic information."""
            return {
                "message": "WavesLab Simulation Environment API",
                "version": "1.0.0",
                "endpoints": {
                    "nodes": "/api/wave-nodes",
                    "specific_node": "/api/wave-nodes/{slug}"
                }
            }

        @self.app.get("/api/wave-nodes", response_model=List[WaveNode], summary="Get all WaveNodes")
        async def get_all_wave_nodes():
            """
            Retrieve all WaveNodes in the system.

            Returns a list of all WaveNodes with their current status and configuration.
            """
            nodes = self.repo.get_all_nodes()
            logger.info(f"Retrieved {len(nodes)} wave nodes")
            return nodes

        @self.app.get("/api/wave-nodes/{slug}", response_model=WaveNode, summary="Get specific WaveNode")
        async def get_wave_node(slug: str):
            """
            Retrieve details of a specific WaveNode by its ID (slug).

            Args:
                slug: The unique ID of the WaveNode

            Returns:
                WaveNode details including current status and configuration

            Raises:
                HTTPException: 404 if the node is not found
            """
            node = self.repo.get_node_by_id(slug)

            if not node:
                logger.warning(f"Node with ID '{slug}' not found")
                raise HTTPException(status_code=404, detail=f"WaveNode with ID '{slug}' not found")

            logger.info(f"Retrieved node '{slug}' details")
            return node

        @self.app.patch("/api/wave-nodes/{slug}", response_model=WaveNode, summary="Update WaveNode endpoint")
        async def update_wave_node(slug: str, update: NodeUpdate):
            """
            Assign or update the endpoint URL of a WaveNode.

            Args:
                slug: The unique ID of the WaveNode
                update: NodeUpdate object containing the new endpoint URL

            Returns:
                Updated WaveNode with the new endpoint URL

            Raises:
                HTTPException: 404 if the node is not found
                HTTPException: 400 if the endpoint URL is invalid
            """
            if not update.endpoint_url:
                logger.error("Endpoint URL is required for update")
                raise HTTPException(status_code=400, detail="endpoint_url is required")

            # Validate the node exists
            node = self.repo.get_node_by_id(slug)
            if not node:
                logger.warning(f"Node with ID '{slug}' not found for update")
                raise HTTPException(status_code=404, detail=f"WaveNode with ID '{slug}' not found")

            # Update the endpoint
            updated_node = self.repo.update_node_endpoint(slug, update.endpoint_url)

            if not updated_node:
                logger.error(f"Failed to update node '{slug}'")
                raise HTTPException(status_code=500, detail="Failed to update node")

            logger.info(f"Updated node '{slug}' endpoint to '{update.endpoint_url}'")
            return updated_node

        @self.app.get("/api/nodes/active", response_model=List[WaveNode], summary="Get active WaveNodes")
        async def get_active_wave_nodes():
            """
            Retrieve all currently active (status='on') WaveNodes.

            This is a convenience endpoint to get only the nodes that are currently
            sending HTTP requests to their endpoints.
            """
            active_nodes = self.repo.get_active_nodes()
            logger.info(f"Retrieved {len(active_nodes)} active nodes")
            return active_nodes

        @self.app.get("/health", summary="Health check endpoint")
        async def health_check():
            """Health check endpoint for monitoring."""
            return {"status": "healthy", "service": "waveslab-api"}

api = WaveLabAPI()