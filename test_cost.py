from src.monitoring.cost import calculate_cost

result = calculate_cost(
    input_tokens=80000,
    output_tokens=2000,
    input_price_per_million=5.0,
    output_price_per_million=15.0
)

print("Input Cost:", result["input_cost"])
print("Output Cost:", result["output_cost"])
print("Total Cost:", result["total_cost"])