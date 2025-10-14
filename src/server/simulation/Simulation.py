import asyncio
from typing import List

import httpx
import logging

from core.model.WaveNode import WaveNode
from core.storage.WavesLabRepository import repository
from server.web_api.NodeRequest import NodeRequest

logger = logging.getLogger(__name__)


class SimulationManager:
    def __init__(self):
        self.client = None
        self.running = None
        self.loop = None
        self._simulation_interval = 30

    async def start(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.running = True
        self.loop = asyncio.create_task(self._simulation_loop())
        logger.info("Simulation loop started")

    async def stop(self):
        """Stop the background task manager."""
        if not self.running:
            return

        self.running = False

        if self.loop:
            self.loop.cancel()
            try:
                await self.loop
            except asyncio.CancelledError:
                pass

        if self.client:
            await self.client.aclose()
            self.client = None

        logger.info("Simulation loop stopped")

    async def _simulation_loop(self):
        while self.running:
            try:
                active_nodes = repository.get_active_nodes()
                if active_nodes:
                    logger.info(f"Processing {len(active_nodes)} active nodes")
                    await self._send_requests_for_nodes(active_nodes)
                else:
                    logger.info("No active nodes to process")

                await asyncio.sleep(self._simulation_interval)
            except asyncio.CancelledError:
                logger.info("Request loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in request loop: {e}")
                await asyncio.sleep(1)  # Brief pause on error

    async def _send_requests_for_nodes(self, nodes: List[WaveNode]):
        tasks = []

        for node in nodes:
            if node.endpoint:
                task = asyncio.create_task(self._send_node_request(node))
                tasks.append(task)
            else:
                logger.info(f"Node '{node.name}' is active but has no endpoint URL")
        if tasks:
            try:
                # Execute all requests concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Log results
                success_count = sum(1 for result in results if result is True)
                error_count = len(results) - success_count

                if success_count > 0:
                    logger.info(f"Successfully sent {success_count} node requests")
                if error_count > 0:
                    logger.warning(f"Failed to send {error_count} node requests")
            except Exception as e:
                logger.error(f"Error in request loop: {e}")

    async def _send_node_request(self, node: WaveNode) -> bool:
        """Send HTTP POST request for a single node."""
        if not self.client:
            logger.info("HTTP client is not initialized")
            return False

        try:
            # Create request payload
            request_data = NodeRequest(
                realTimeConsumption=node.real_time_consumption,
                username=node.assigned_user,
            )

            # Send POST request
            response = await self.client.post(
                node.endpoint,
                json=request_data.model_dump(mode='json'),
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Request sent successfully for node '{node.name}' to {node.endpoint}")
                return True
            else:
                logger.info(f"Request failed for node '{node.name}': HTTP {response.status_code}")
                return False

        except httpx.TimeoutException:
            logger.info(f"Request timeout for node '{node.name}' to {node.endpoint}")
            return False
        except httpx.RequestError as e:
            logger.info(f"Network error for node '{node.name}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending request for node '{node.name}': {e}")
            return False

simulation = SimulationManager()