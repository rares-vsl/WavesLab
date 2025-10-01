# WavesLab Simulation Environment

**WavesLab** is a simulation environment that models a household equipped with virtual occupants and smart furniture
hookups, called **WaveNodes**.
Each **WaveNode** represents a furniture connection that delivers a single utility (electricity, water, or gas) when
active.

---

### WaveNode

A WaveNode has the following attributes:

* **id** – a slugified version of the name.
* **name** – unique human-readable identifier.
* **node_type** – one of three types: `electricity`, `water`, or `gas`.
* **endpoint_url** – the destination URL where data is transmitted.
* **status** – indicates whether the node is active (`on`) or inactive (`off`).
* **provision_rate** – numeric value representing the amount of utility delivered.

---

### VirtualUser

* **username** – unique name for a simulated occupant.

---

### Command Line Interface (CLI)

The simulation entities are controlled via a CLI. It supports starting and stopping WaveNodes, as well as associating
them with users.

**Commands:**

* `wavelab start <node_name> [--user <user_name>]`

    * If the node is not found: exit with non-zero status.
    * If a user is specified: associate the user’s token for outgoing requests.
    * If the node is already running: print `already running` and exit with status `0`.

* `wavelab stop <node_name>`

    * If the node is not found: exit with non-zero status.
    * If the node is already stopped: print `already stopped` and exit with status `0`.

---

### Server & API

The environment includes a server that exposes a simple REST API:

* **GET** `/api/wave-nodes`: retrieve all nodes.
* **GET** `/api/wave-nodes/{slug}`: retrieve details of a specific node.
* **PATCH** `/api/wave-nodes/{slug}`: assign or update the endpoint of a node.

---

### Node Behavior

* Every **5 seconds**, each active node automatically sends an HTTP `POST` request to its `endpoint_url`.
* The request payload includes:
    * the node’s `provision_rate`, and
    * the associated user’s `username` (if one is assigned).
* For simplicity, the system uses a **single loop** to trigger these requests across all active nodes.

---

### Scope & Simplifications

* Node and user management (creation, deletion) is out of scope.
* Only status toggling, endpoint assignment, and user association are supported.
* For data storage JSON file are used. 

