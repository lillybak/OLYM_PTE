Here’s what I found about **RAGAS support for multiple-choice questions (MCQs) with ground truth**:

---

## 🔍 How RAGAS Evaluates MCQs with Ground Truth

### 📌 1. Support for `ground_truths`

RAGAS allows MCQ-style evaluation by leveraging the `ground_truths` field in each evaluation sample. While RAGAS originally focused on reference-free evaluation, it now **supports metrics that rely on human-provided ground-truth labels**, such as **context\_recall** and **answer\_correctness**.
([Medium][1])

* `context_recall` requires the ground truth answer to assess whether your retrieval mechanism brought in all necessary information.
* Other metrics—like **faithfulness** and **answer\_relevancy**—can still be used even without ground truth.

---

### ⚙️ 2. RAGAS Sample Structure & Classes

RAGAS uses structured sample classes:

* For MCQs and single-question interactions, use **`SingleTurnSample`**
* It accepts:

  * `user_input` (question)
  * `retrieved_contexts` (list of context chunks)
  * `response` (the generated answer)
  * `reference` or `ground_truth` (the correct answer)
  * Optionally, `rubric` for evaluation labels
    ([docs.ragas.io][2], [Langfuse][3], [docs.ragas.io][4])

#### Sample Code:

```python
from ragas import SingleTurnSample

sample = SingleTurnSample(
  user_input="Which muscle initiates shoulder abduction?",
  retrieved_contexts=["The supraspinatus initiates the first 15°..."],
  response="The supraspinatus initiates the first 15° of movement.",
  reference="The supraspinatus initiates the first 15° of movement."
)
```

---

### 📊 3. Running Evaluation

Use the `evaluate` function with appropriate metrics:

```python
from ragas import evaluate
from ragas.metrics import (
    context_recall, context_precision,
    faithfulness, answer_relevancy, answer_correctness
)

result = evaluate(
  [sample],
  metrics=[
    context_precision,
    faithfulness,
    answer_relevancy,
    context_recall,
    answer_correctness
  ]
)
```

This yields component-level scores.
([docs.ragas.io][2], [Developer Portal | Couchbase][5])

---

## ✅ Summary Table

| Field                | Description                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| `user_input`         | The MCQ question or prompt                                                                           |
| `retrieved_contexts` | Retrieved document snippets                                                                          |
| `response`           | Model's answer / selected choice                                                                     |
| `reference`          | Correct answer (ground truth) for context\_recall & correctness                                      |
| Metrics              | e.g. `faithfulness`, `answer_relevancy`, `answer_correctness`, `context_recall`, `context_precision` |

---

## 🧠 In Your Use Case

Yes—you can absolutely evaluate MCQs with RAGAS by doing the following:

1. Construct a list of `SingleTurnSample` instances with:

   * Generated question
   * Retrieved context snippet
   * Model-generated answer
   * The correct answer from ground truth
2. Call `evaluate(...)` with relevant metrics including `answer_correctness` and `context_recall`
3. Inspect the resulting scores to diagnose retrieval or generation issues

---

Would you like me to help generate a small batch of `SingleTurnSample` objects from your manual dataset and show how to call `evaluate(...)` with your synthetic samples? Let me know!

[1]: https://medium.com/data-science/evaluating-rag-applications-with-ragas-81d67b0ee31a?utm_source=chatgpt.com "Evaluating RAG Applications with RAGAs"
[2]: https://docs.ragas.io/en/v0.1.21/getstarted/evaluation.html?utm_source=chatgpt.com "Evaluating Using Your Test Set"
[3]: https://langfuse.com/guides/cookbook/evaluation_of_rag_with_ragas?utm_source=chatgpt.com "Evaluation of RAG pipelines with Ragas"
[4]: https://docs.ragas.io/en/v0.2.8/concepts/components/eval_sample/?utm_source=chatgpt.com "Evaluation Sample"
[5]: https://developer.couchbase.com/tutorial-evaluate-rag-responses-using-ragas/?utm_source=chatgpt.com "Tutorial - Evaluate RAG Responses using Ragas"

