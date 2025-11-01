from itertools import combinations

class WisRuleWithNegative:
    def __init__(self, transactions, min_support=0.2, min_confidence=0.5):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.item_support = {}
        self.rules = []

    def generate_frequent_itemsets(self):
        item_counts = {}
        total_transactions = len(self.transactions)

        for transaction in self.transactions:
            for item in transaction:
                item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1

        # Filter by minimum support
        self.item_support = {
            item: count / total_transactions
            for item, count in item_counts.items()
            if count / total_transactions >= self.min_support
        }

        # Generate larger itemsets
        current_itemsets = list(self.item_support.keys())
        k = 2

        while current_itemsets:
            new_candidates = [
                i.union(j) for i in current_itemsets for j in current_itemsets
                if len(i.union(j)) == k
            ]
            candidate_counts = {candidate: 0 for candidate in new_candidates}

            for transaction in self.transactions:
                transaction_set = frozenset(transaction)
                for candidate in new_candidates:
                    if candidate.issubset(transaction_set):
                        candidate_counts[candidate] += 1

            current_itemsets = []
            for candidate, count in candidate_counts.items():
                support = count / total_transactions
                if support >= self.min_support:
                    self.item_support[candidate] = support
                    current_itemsets.append(candidate)

            k += 1

    def generate_rules(self):
        for itemset in self.item_support.keys():
            if len(itemset) > 1:
                for subset in self.powerset(itemset):
                    if subset and subset != itemset:
                        antecedent = frozenset(subset)
                        consequent = itemset - antecedent
                        self.evaluate_rule(antecedent, consequent, positive=True)
                        self.evaluate_rule(antecedent, consequent, positive=False)

    def evaluate_rule(self, antecedent, consequent, positive=True):
        if not consequent:
            return

        total_transactions = len(self.transactions)
        antecedent_support = self.item_support.get(antecedent, 0)
        consequent_support = self.item_support.get(consequent, 0)

        if positive:
            confidence = antecedent_support
            rule_type = "Positive"
        else:
            complement_support = 1 - consequent_support
            confidence = antecedent_support * complement_support
            rule_type = "Negative"

        if confidence >= self.min_confidence:
            rule = (antecedent, "¬" if not positive else "", consequent, confidence, rule_type)
            self.rules.append(rule)

    def print_rules(self):
        print("\nAssociation Rules (Positive and Negative):")
        if not self.rules:
            print("No rules meet the support and confidence thresholds.")
            return

        for antecedent, negation, consequent, confidence, rule_type in self.rules:
            print(f"{set(antecedent)} => {negation}{set(consequent)} ({rule_type}, Confidence: {confidence:.2f})")

    @staticmethod
    def powerset(itemset):
        """Returns all non-empty subsets of a set."""
        return [set(comb) for i in range(1, len(itemset)) for comb in combinations(itemset, i)]


# Example Transactions
transactions = [
    ['Milk', 'Bread', 'Butter'],
    ['Bread', 'Butter'],
    ['Milk', 'Eggs', 'Butter'],
    ['Milk', 'Bread'],
    ['Eggs', 'Butter'],
    ['Milk', 'Grapes'],
    ["Milk", "Bread", "Butter", "Eggs"]
]

# Initialize WisRule and execute
wisrule = WisRuleWithNegative(transactions, min_support=0.2, min_confidence=0.4)
wisrule.generate_frequent_itemsets()
wisrule.generate_rules()
wisrule.print_rules()
