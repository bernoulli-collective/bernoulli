# Landmark Papers and Non-Standard Representations in Researcher Agents

## Executive summary

Researcher agents did not arise only from recent context engineering. Their deeper undercurrents run through older AI traditions: scientific-discovery systems, blackboard architectures, classical planning, cognitive architectures, tool-using assistants, and explicit search over structured intermediate states.[1][2][3][4][5][6][7][8] In the LLM era, the most influential papers did not merely make prompts longer; they made agent state more structured.[9][10][11][12][13][14]

The clearest landmarks fall into three groups. First are **enabling mechanism papers** such as *Toolformer* (2023), *ReAct* (2023), *Tree of Thoughts* (2023), *Generative Agents* (2023), *Voyager* (2023), and *Graph of Thoughts* (2024), which introduced or consolidated explicit tool use, action-observation trajectories, search trees/graphs, layered memory, and reusable skill libraries.[9][10][11][12][13][14] Second are **end-to-end researcher or scientist systems** such as *The AI Scientist* (2024), *SciAgents* (2024), *Agent Laboratory* (2025), and *DeepResearcher* (2025), which assemble those ingredients into research workflows.[15][16][17][18] Third are **benchmark and survey papers** such as *AutoResearchBench* (2026), DeepResearch Bench, and AstaBench, which show that current systems remain weak at real scientific literature discovery and research-grade completeness.[19][20][21][22]

The strongest unifying theme is the importance of **non-standard representations**: external blackboards, task graphs, action-observation trajectories, memory streams, thought trees or graphs, executable skill libraries, workflow-state machines, ontological graphs, and candidate-set/provenance structures.[3][4][5][6][10][11][12][13][16][17][18][19] These representations move crucial state **outside** a flat text window. That is the real conceptual alternative to pure context engineering.

The evidence base is mixed. Some representational ideas have strong support on planning or agent-behavior tasks: *Tree of Thoughts* reports a jump on Game of 24 from 4% with chain-of-thought to 74% with ToT, *Graph of Thoughts* reports better task quality than ToT on its tasks, *Generative Agents* reports ablations for observation/planning/reflection, and *Voyager* reports large gains from its skill-library design.[11][12][13][14] But direct evidence that these representations improve **end-to-end scientific research quality** is still limited. Recent deep-research benchmarks suggest that even frontier agents remain far from robust autonomous literature discovery.[18][19][20][21][22] So the cautious conclusion is: non-standard representations matter, but their strongest direct evidence is still stronger for **control, search, memory, and tool use** than for full autonomous science.

## 1. What are the landmark papers?

### 1.1 Foundational undercurrents before the LLM era

A serious history of researcher agents should begin before LLM agents.

**Scientific-discovery systems** are one important origin. *Heuristic DENDRAL* (1968) and the later retrospective *DENDRAL: A Case Study of the First Expert System for Scientific Hypothesis Formation* (1993) framed scientific work as structured hypothesis search rather than generic text retrieval.[1][2] The BACON line, including *BACON: A Production System That Discovers Empirical Laws* (1977) and *BACON.5: The Discovery of Conservation Laws* (1981), represented discovery as iterative search over descriptions and regularities.[7][8]

A second origin is the **blackboard tradition**. *A Multi-Level Organization for Problem Solving Using Many, Diverse, Cooperating Sources of Knowledge* (1975) and *A Retrospective View of the HEARSAY-II Architecture* (1977) introduced shared external problem state across specialized processes.[3][4] *BB1: an Architecture for Blackboard Systems that Control, Explain, and Learn About Their Own Behavior* (1984) is especially notable because it adds a domain blackboard, a control blackboard, control plans, explanations of actions, and learning of control heuristics.[6] In modern language, that looks like an external scratchpad plus control state plus self-monitoring.

A third origin is **planning and cognitive architecture** work. Classical planning treated problem solving as search over states and operators, while systems such as Soar modeled behavior as movement through problem spaces with working memory, subgoals, and differentiated memory systems.[5] Even when modern papers do not cite these traditions directly, their representational logic survives in many researcher-agent designs.

### 1.2 LLM-era bridge papers

Several 2023 papers created the technical substrate for researcher agents.

- **Toolformer: Language Models Can Teach Themselves to Use Tools** (Schick et al., 2023) made external API use a learned, structured behavior rather than an ad hoc prompt trick.[9]
- **ReAct: Synergizing Reasoning and Acting in Language Models** (Yao et al., 2023) made action-observation trajectories first-class, interleaving reasoning traces with tool use.[10]
- **Tree of Thoughts: Deliberate Problem Solving with Large Language Models** (Yao et al., 2023) replaced single-path reasoning with deliberate search over intermediate states.[11]
- **Generative Agents: Interactive Simulacra of Human Behavior** (Park et al., 2023) normalized persistent memory streams, higher-level reflections, and dynamic retrieval for planning.[13]
- **Voyager: An Open-Ended Embodied Agent with Large Language Models** (Wang et al., 2023) showed that reusable executable skills can become a durable representation of accumulated capability.[14]
- **Graph of Thoughts: Solving Elaborate Problems with Large Language Models** (Besta et al., 2024) generalized thought structure from trees to arbitrary graphs.[12]

These papers are not all "researcher agent" papers in the narrow sense. But they are landmarks because later researcher agents reuse their ingredients.[9][10][11][12][13][14]

### 1.3 Researcher-agent and scientist-agent papers

The end-to-end research papers are newer and the canon is still unsettled.

- **The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery** (Lu et al., 2024) is a landmark candidate because it attempts to automate idea generation, code writing, experiment execution, visualization, paper writing, and review.[15]
- **SciAgents: Automating Scientific Discovery Through Multi-Agent Intelligent Graph Reasoning** (Ghafarollahi and Buehler, 2024) is a landmark candidate because it puts ontological knowledge graphs and graph reasoning at the center of scientific discovery support.[16]
- **Agent Laboratory: Using LLM Agents as Research Assistants** (Schmidgall et al., 2025) is a landmark because it explicitly stages the workflow into literature review, experimentation, and report writing.[17]
- **DeepResearcher: Scaling Deep Research via Reinforcement Learning in Real-world Environments** (Zheng et al., 2025) is a landmark because it argues that prompt engineering is not enough and trains deep-research behavior end-to-end in live web environments.[18]

### 1.4 Benchmark papers matter because the field is young

In a mature field, benchmark papers are not the same as landmark systems. In researcher agents, the field is still young enough that evaluation papers also shape the canon.

- **AutoResearchBench: Benchmarking AI Agents on Complex Scientific Literature Discovery** (2026) is important because it isolates literature discovery as a hard core capability of autonomous research.[19]
- **DeepResearch Bench** and **AstaBench** matter because they treat deep research and scientific-research ability as distinct system classes worth benchmarking holistically.[20][21][22]
- **A Comprehensive Survey of Deep Research** (2025) is useful as a taxonomy and landscape survey, though it is not itself a landmark technical contribution.[23]

## 2. What counts as a non-standard representation?

The most useful distinction is not "prompting vs not prompting." It is whether the system’s important state is represented only as a flat text prefix or whether key state lives in some more structured form.

### 2.1 External blackboards, ledgers, and shared notebooks

Blackboard systems already treated problem solving as operations over a shared external state.[3][4][6] Modern equivalents include task ledgers, lab notebooks, explicit plans, and shared memory buffers among agents. The innovation here is not more context, but a **persistent workspace** that multiple procedures or agents can inspect and update.

### 2.2 Action-observation trajectories

*ReAct* made trajectories of reasoning, action, and observation a central representation.[10] This matters because the agent is no longer a one-shot text predictor. It becomes a controller operating over a typed interaction history with the world.

### 2.3 Trees and graphs of intermediate states

*Tree of Thoughts* and *Graph of Thoughts* are clear departures from flat prompting.[11][12] They represent reasoning as search over intermediate states that can branch, backtrack, merge, or form dependency graphs. For researcher agents, these ideas matter because literature discovery, evidence integration, and hypothesis development are naturally non-linear.

### 2.4 Memory streams, reflections, and layered retrieval

*Generative Agents* and *Reflexion* introduced layered memory designs in which experiences are stored durably, abstracted into reflections, and dynamically retrieved for future planning.[13][24] This is not equivalent to dumping old transcript text into the prompt. It adds a policy for what to retain, abstract, and recall.

### 2.5 Reusable executable skill libraries

*Voyager* represents learned capabilities as executable code skills in an ever-growing library.[14] This is especially relevant to researcher agents that repeatedly perform literature search, parsing, experiment setup, and evaluation subtasks.

### 2.6 Tool-call schemas and typed actions

*Toolformer* and *DeepResearcher* both rely on structured tool interfaces.[9][18] *DeepResearcher* is especially explicit: search and browsing are represented as JSON-format tool calls, and a dedicated browsing agent maintains short-term memory for reading webpages.[18] These structured actions are representational choices, not merely prompt choices.

### 2.7 Research workflow states

*Agent Laboratory* and *The AI Scientist* both organize research into explicit stages such as literature review, experimentation, and writing.[15][17] This gives the system a typed workflow state rather than a single undifferentiated "answer the question" objective.

### 2.8 Ontological and evidence graphs

*SciAgents* is the clearest example of a representation that is genuinely different from context engineering. It uses large-scale ontological knowledge graphs to organize scientific concepts and support multi-agent graph reasoning.[16] This moves the agent closer to operating over an explicit scientific concept structure.

### 2.9 Candidate sets, completeness, and provenance structures

Researcher agents also need representations for candidate papers, answer sets, evidence support, and stopping criteria. *AutoResearchBench* makes this visible by defining tasks over singleton answer sets or exhaustive literature sets.[19] That benchmark implicitly argues that a serious researcher agent needs internal structures for completeness, boundaries, and evidence provenance.

## 3. Which ideas are genuinely beyond context engineering?

A good rule of thumb is:

- **Mostly context engineering:** adding more snippets, stuffing more papers into the prompt, or summarizing old context without changing the state structure.
- **Representation innovation:** explicit memory layers, search trees, dependency graphs, executable skills, typed tool calls, candidate sets, workflow-state machines, and ontological graphs.[6][9][10][11][12][13][14][16][17][18][19]

By that standard, the most genuine representational innovations in this literature are:

1. **Search-structured intermediate states** (*Tree of Thoughts*, *Graph of Thoughts*).[11][12]
2. **Durable memory with abstraction and retrieval** (*Generative Agents*, *Reflexion*).[13][24]
3. **Structured action schemas and trajectories** (*Toolformer*, *ReAct*, *DeepResearcher*).[9][10][18]
4. **Reusable external skill or program libraries** (*Voyager*).[14]
5. **Explicit workflow-state representations** (*Agent Laboratory*, *The AI Scientist*).[15][17]
6. **Knowledge-graph / ontology-grounded structures** (*SciAgents*).[16]

## 4. What evidence do we have that these representations help?

### 4.1 Stronger evidence: control, planning, and search

The strongest evidence is still on focused tasks rather than full scientific discovery.

*Tree of Thoughts* reports a large improvement on Game of 24, from 4% with chain-of-thought prompting to 74% with ToT.[11] *Graph of Thoughts* reports better task quality than ToT on its benchmarks, including a 62% quality increase on sorting while reducing cost.[12] These are substantial effects, but they are evidence about search-structured reasoning more than about autonomous research directly.

### 4.2 Stronger evidence: memory and reusable capability

*Generative Agents* reports ablation evidence that observation, planning, and reflection each contribute to believable agent behavior.[13] *Voyager* reports large gains associated with its reusable skill library: 3.3x more unique items, 2.3x longer travel distance, and up to 15.3x faster progress on key milestones than prior approaches.[14] Again, these are not literature-review benchmarks, but they support the broader claim that structured external memory and reusable programs can materially matter.

### 4.3 Better evidence for deep-research agents: real-world environment training

Among explicitly deep-research systems, *DeepResearcher* offers one of the stronger pieces of evidence. It reports improvements of up to 28.9 points over prompt-engineering baselines and up to 7.2 points over RAG-based RL agents.[18] The paper’s central claim is that training in real web environments, with explicit trajectories and browsing-agent memory, matters in a way that static retrieval setups do not.[18]

This does not isolate representation alone as the sole cause. But it supports a broader thesis: research agents benefit from richer interaction state and environment-grounded control, not just better prompts.[18]

### 4.4 Weaker evidence for end-to-end science

*Agent Laboratory* and *The AI Scientist* show that structured research workflows are feasible.[15][17] *Agent Laboratory* reports reduced cost and benefits from human feedback.[17] *The AI Scientist* demonstrates a full loop from idea generation to simulated review.[15] But these papers do not yet decisively prove that specific representational choices are what drive the gains, as opposed to stronger models, better tools, or workflow decomposition itself.

### 4.5 Strong caution from benchmarks

The strongest negative evidence comes from evaluation papers. *AutoResearchBench* reports that frontier models achieve only **9.39%** accuracy on its Deep Research task and **9.31%** IoU on its Wide Research task.[19] It also argues that extra turns and more tool calls often bring only limited gains.[19]

That matters for this review. It means we should not overstate what current researcher agents can do. The field has many elegant representational proposals, but benchmark evidence says robust scientific literature discovery is still largely unsolved.[19][20][21][22]

## 5. Main caveats and disagreements

### 5.1 The canon is still unstable

Many 2024–2026 papers are landmark candidates rather than universally accepted classics. The field is moving too quickly to pretend a settled canon already exists.[15][16][17][18][19][23]

### 5.2 Benchmarks and real research are not the same

Papers like *Tree of Thoughts* and *Graph of Thoughts* show strong benefits on reasoning tasks, but those results do not automatically transfer to real scientific research workflows.[11][12]

### 5.3 Representation gains are confounded

When a paper claims improvement, likely confounds include stronger base models, better tools, more retrieval coverage, more compute or more trajectories, human feedback, and better environment design.[15][17][18][19][23]

### 5.4 Some attractive ideas remain under-tested

Graph memory, provenance graphs, workflow ledgers, and ontology-driven systems are conceptually compelling, but they often lack clean ablations on end-to-end research outcomes.[16][18][19][23]

## 6. Open questions

1. Which non-standard representations best improve **scientific correctness**, not just task completion?
2. How should researcher agents represent **completeness** and stopping conditions in literature discovery?
3. Do ontology graphs or evidence graphs outperform simpler memory stores on real scientific tasks?
4. What is the right split between internal latent reasoning and external explicit state?
5. When does multi-agent decomposition genuinely help, rather than just adding overhead?
6. Can benchmark suites cleanly separate gains from representation from gains from larger models or better tools?

## 7. Bottom line

The deepest innovative trail behind researcher agents is a story about **structured external state**. Long before context engineering became fashionable, AI already explored hypothesis spaces, blackboards, control plans, problem spaces, and explicit memory systems.[1][2][3][4][5][6][7][8] The LLM era revived those ideas in new forms: tool trajectories, thought trees, graph-structured reasoning, reflective memory, executable skill libraries, workflow-state machines, and ontology graphs.[9][10][11][12][13][14][15][16][17][18]

So the best answer is not that researcher agents are mainly a triumph of context engineering. The more fundamental story is that they are reassembling old AI ideas about **how to represent research state**—and only partly succeeding so far. The field’s strongest papers show that these representations help with planning, memory, search, and tool use.[9][10][11][12][13][14][18] The field’s strongest benchmarks show that autonomous scientific research remains far from solved.[19][20][21][22]

## Sources

[1] Heuristic DENDRAL - A program for generating explanatory hypotheses in organic chemistry (1968). https://ntrs.nasa.gov/citations/19680054644

[2] DENDRAL: A case study of the first expert system for scientific hypothesis formation (1993 retrospective / archive page). https://deepblue.lib.umich.edu/handle/2027.42/30758

[3] A Multi-Level Organization for Problem Solving Using Many, Diverse, Cooperating Sources of Knowledge (IJCAI 1975). https://ijcai.org/Proceedings/75/Papers/072.pdf

[4] A Retrospective View of the HEARSAY-II Architecture (IJCAI 1977). https://ijcai.org/Proceedings/77-2/Papers/055.pdf

[5] AI planning: systems and techniques. https://scispace.com/pdf/ai-planning-systems-and-techniques-1i9i48ewhi.pdf

[6] BB1: an architecture for blackboard systems that control, explain, and learn about their own behavior (1984). http://infolab.stanford.edu/TR/CS-TR-84-1034.html

[7] BACON: A Production System That Discovers Empirical Laws (1977). https://www.ijcai.org/Proceedings/77-1/Papers/057.pdf

[8] BACON.5: The Discovery of Conservation Laws (1981). https://ijcai.org/Proceedings/81-1/Papers/025.pdf

[9] Toolformer: Language Models Can Teach Themselves to Use Tools (2023). https://arxiv.org/abs/2302.04761

[10] ReAct: Synergizing Reasoning and Acting in Language Models (2023). https://arxiv.org/abs/2210.03629

[11] Tree of Thoughts: Deliberate Problem Solving with Large Language Models (2023). https://arxiv.org/abs/2305.10601

[12] Graph of Thoughts: Solving Elaborate Problems with Large Language Models (2024). https://arxiv.org/abs/2308.09687

[13] Generative Agents: Interactive Simulacra of Human Behavior (2023). https://arxiv.org/abs/2304.03442

[14] Voyager: An Open-Ended Embodied Agent with Large Language Models (2023). https://arxiv.org/abs/2305.16291

[15] The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery (2024). https://arxiv.org/abs/2408.06292

[16] SciAgents: Automating scientific discovery through multi-agent intelligent graph reasoning (2024). https://arxiv.org/abs/2409.05556

[17] Agent Laboratory: Using LLM Agents as Research Assistants (2025). https://arxiv.org/abs/2501.04227

[18] DeepResearcher: Scaling Deep Research via Reinforcement Learning in Real-world Environments (2025). https://arxiv.org/html/2504.03160v4

[19] AutoResearchBench: Benchmarking AI Agents on Complex Scientific Literature Discovery (2026). https://arxiv.org/html/2604.25256

[20] DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents. https://deepresearch-bench.github.io/

[21] AstaBench: Rigorous benchmarking of AI agents with a scientific research suite. https://allenai.org/papers/astabench

[22] AstaBench arXiv page. https://arxiv.org/abs/2510.21652

[23] A Comprehensive Survey of Deep Research: Systems, Methodologies, and Applications (2025). https://arxiv.org/html/2506.12594v1

[24] Reflexion: Language Agents with Verbal Reinforcement Learning (2023). https://arxiv.org/abs/2303.11366
