# Diagnostic Demo Queries

This document contains the diagnostic demo questions and Cypher queries used to retrieve relevant fault-diagnosis subgraphs from Neo4j.

The natural-language questions were manually translated into Cypher queries for demonstration purposes.

\begin{longtable}{p{0.7cm} p{5.2cm} p{8.0cm}}
\caption{Diagnostic demo questions and Cypher queries used to retrieve relevant fault-diagnosis subgraphs from Neo4j.}
\label{tab:diagnostic_demo_questions} \\
\toprule
\textbf{No.} & \textbf{Diagnostic Question} & \textbf{Cypher Query} \\
\midrule
\endfirsthead

\toprule
\textbf{No.} & \textbf{Diagnostic Question} & \textbf{Cypher Query} \\
\midrule
\endhead

\midrule
\multicolumn{3}{r}{\textit{(Continued on next page)}} \\
\midrule
\endfoot

\bottomrule
\endlastfoot

1 &
Welke actie is geprobeerd toen de filamenten traag startten?

Eng:

What action was tried when the filaments started slowly?
&
{\scriptsize\ttfamily
MATCH p=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fl.name) CONTAINS 'armkanteling'\newline
AND toLower(fs.description) CONTAINS 'shutterpositie'\newline
OPTIONAL MATCH pr=(fs)-[:CAUSED\_BY]->(fr:FaultReason)\newline
OPTIONAL MATCH pm=(fs)-[r:MITIGATED\_BY]->(fm:FaultMeasure)\newline
RETURN p, pr, pm, fl.name, fs.description, fr.name, fm.description, r.resolution\_status, fs.case\_ids\newline
LIMIT 5;
}
\\

2 &
Welke actie is geprobeerd toen de filamenten traag startten?

Eng:

What action was tried when the filaments started slowly?
&
{\scriptsize\ttfamily
MATCH p=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fl.name) CONTAINS 'filamenten'\newline
AND toLower(fs.description) CONTAINS 'traag'\newline
OPTIONAL MATCH pm=(fs)-[r:MITIGATED\_BY]->(fm:FaultMeasure)\newline
RETURN p, pm, fl.name, fs.description, fm.description, r.resolution\_status, fs.case\_ids\newline
LIMIT 5;
}
\\

3 &
De rotatietafel vindt zijn nulpositie niet of homing lukt niet. Wat moet ik controleren?

Eng:

The rotation table cannot find its zero position or homing fails. What should I check?
&
{\scriptsize\ttfamily
MATCH p1=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE (\newline
toLower(fs.description) CONTAINS 'nulpositie'\newline
OR toLower(fs.description) CONTAINS 'homing'\newline
)\newline
AND (\newline
toLower(fl.name) CONTAINS 'rotatietafel'\newline
OR toLower(fl.name) CONTAINS 'rotatie tafel'\newline
OR toLower(fl.name) CONTAINS 'tafel'\newline
)\newline
OPTIONAL MATCH p2=(fs)-[:CAUSED\_BY]->(fr:FaultReason)\newline
OPTIONAL MATCH p3=(fs)-[r:MITIGATED\_BY]->(fm:FaultMeasure)\newline
RETURN p1, p2, p3
}
\\

4 &
What causes CB1 to trip immediately when the compressor is switched ON?
&
{\scriptsize\ttfamily
MATCH p1=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fs.description) CONTAINS 'trips immediately'\newline
OPTIONAL MATCH p2=(fs)-[:CAUSED\_BY]->(fr:FaultReason)\newline
OPTIONAL MATCH p3=(fs)-[r:MITIGATED\_BY]->(fm:FaultMeasure)\newline
RETURN p1, p2, p3
}
\\

5 &
What should be checked when the compressor stops after several minutes of operation?
&
{\scriptsize\ttfamily
MATCH p1=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fl.name) CONTAINS 'compressor'\newline
AND toLower(fs.description) CONTAINS 'several minutes'\newline
AND toLower(fs.description) CONTAINS 'stops'\newline
OPTIONAL MATCH p3=(fs)-[r:MITIGATED\_BY]->(fm:FaultMeasure)\newline
RETURN p1, p3
}
\\

6 &
Why are On-Board IS cryopumps not visible on IS Controller screens?
&
{\scriptsize\ttfamily
MATCH p1=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fl.name) CONTAINS 'helix'\newline
AND toLower(fs.description) CONTAINS 'not visible'\newline
AND toLower(fs.description) CONTAINS 'is controller'\newline
OPTIONAL MATCH p2=(fs)-[:CAUSED\_BY]->(fr:FaultReason)\newline
RETURN p1, p2
}
\\

7 &
What does an INTERLOCK LED flashing indicate on the Ion Beam Drive system?
&
{\scriptsize\ttfamily
MATCH p1=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fs.description) CONTAINS 'interlock led flashing'\newline
OPTIONAL MATCH p2=(fs)-[:CAUSED\_BY]->(fr:FaultReason)\newline
RETURN p1, p2
}
\\

8 &
What should be checked when the On-Board cryopump has no display?
&
{\scriptsize\ttfamily
MATCH p1=(fl:FaultLocation)-[:HAS\_FAULT]->(fs:FaultSymptom)\newline
WHERE toLower(fs.description) CONTAINS 'no display'\newline
OPTIONAL MATCH p3=(fs)-[r:MITIGATED\_BY]->(fm:FaultMeasure)\newline
RETURN p1, p3
}
\\

\end{longtable}
