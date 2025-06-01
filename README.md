# cyberprojects
cybersecurity inspired projects

## Supercar Rental Agent

This repository includes a simple command-line assistant for managing
supercar rental inquiries. Run the agent with Python:

```bash
python3 supercar_agent/agent.py
```

The agent will:

1. Collect rental dates, location, and driver info.
2. Check a mock inventory defined in `inventory.json`.
3. Generate a price quote and deposit amount.
4. Provide a placeholder payment link.
5. Save all leads to `leads.csv` for follow-up.

Inventory details are stored in `supercar_agent/inventory.json` and can be
customized as needed.
