import itertools

def get_candidate_set(previous_itemsets):
    """Generate candidate itemsets from the previous level."""
    return list(itertools.combinations(previous_itemsets, 2))

def get_subsets(dataset, min_support):
    """Extract subsets that satisfy minimum support."""
    subsets = []
    for itemset in dataset:
        if itemset['support'] >= min_support:
            subsets.append(itemset)
    return subsets

def adjust_utility(Ui, Ua):
    """Adjust utility when the context variable exceeds normal range."""
    return Ui + Ua

def getUPII(U_A_B, supp_A_B, U_A, supp_A, U_B, supp_B):
    """Compute Utility-based Positive Interestingness Index (UPII)."""
    return (U_A_B * supp_A_B - U_A * supp_A * U_B * supp_B) / (U_A * supp_A * (1 - supp_B))

def wise_association_rule_mining(dataset, context_variable, abnormal_context, Ua, min_support, min_confidence, min_utility, min_interestingness):
    """Main function to extract wise positive and negative frequent itemsets."""
    WFISp, WFISn = set(), set()
    
    for i, location in enumerate(dataset):
        # Convert dictionaries to hashable tuples (e.g., using frozenset)
        location = set(tuple(frozenset(item.items())) for item in location) 
        
        candidate_set = get_candidate_set(location)
        
        for obj in dataset:
            subsets = get_subsets(obj, min_support)
            for itemset in subsets:
                itemset.setdefault('count', 0) 
                itemset['count'] += 1
        
        if context_variable == abnormal_context:
            adjust_utility(Ua, Ua)
        
        # Calculate Nj with hashable tuples
        Nj = set(candidate_set) - location 
        
        # Filter based on interestingness
        location = {tuple(frozenset(m.items())) for m in location if m.get('interestingness', 0) >= min_interestingness}
        WFISp |= location
        
        Nj = {tuple(frozenset(n.items())) for n in Nj if n.get('interestingness', 0) >= min_interestingness}
        WFISn |= Nj
    
    return WFISp, WFISn

# Example dataset
dataset = [
    [{'item': 'A', 'support': 0.4, 'utility': 10, 'interestingness': 0.8},
     {'item': 'B', 'support': 0.3, 'utility': 8, 'interestingness': 0.7}],
    [{'item': 'C', 'support': 0.5, 'utility': 12, 'interestingness': 0.9},
     {'item': 'D', 'support': 0.2, 'utility': 5, 'interestingness': 0.6}]
]

WFISp, WFISn = wise_association_rule_mining(
    dataset, context_variable='Temperature', abnormal_context='High',
    Ua=5, min_support=0.2, min_confidence=0.5, min_utility=5, min_interestingness=0.7
)

print("Wise Positive Frequent Itemsets:", WFISp)
print("Wise Negative Frequent Itemsets:", WFISn)