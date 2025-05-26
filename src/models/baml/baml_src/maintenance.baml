// Defining a data model.

enum Machine {
  IBM3
  IBM4
}

class FaultLocation {
  name string
  machine Machine?
}

class FaultReason {
  name string
}
class FaultMeasure {
  description string
}
// Resolution status applies to the relation FaultSymptom → FaultMeasure
enum ResolutionStatus {
  Resolved
  Unknown
}

class FaultReport {
  fault_location FaultLocation
  fault_symptoms string[]
  fault_reason FaultReason[]
  fault_measures FaultMeasure[]
  resolution_status ResolutionStatus
}

function ExtractFaultInfo(log_text: string) -> FaultReport {
  client CustomGPT4o
  prompt #"
    You are an expert in analyzing technical maintenance logs.
 
    Extract the following entities:
    - fault_location: the component with issue (add machine: IBM3/IBM4 if mentioned)
    - fault_symptoms: all observable problems or symptoms.
    - fault_reason: the stated causes of the issue (if any) + certainty
    - fault_measures: steps taken to resolve the issue + resolution_status

    Here are examples of extracting structured data:

    Examples 1:
        log_text: "Case-ID: IBM3_C22_03-Aug-16_04-Aug-16\nSources: storing, Storing, reparatie\nIssues:\n- Probleem: Beamcurrent tussen 300 - 200mA  (als je langzaam met de hand zakt tot 150mA)  Niet lager.        | Beamboard getest. Lijkt te werken. Beamcurrent start op een hoge waarde (ca. 300mA) en zakt langzaam.          | Besturing gaat door bij 200mA (Phaco) maar niet bij 100 mA Infinera). Schakelt af op \"\"out of tollerance\"\".         | Oorzaak: Comdel CX-600S generator  (SN 31141315)   (11-6-2000)        \n- Niet goed Generator Comdel CX-600S  SN 31141315    part: FP3114RB         | Werkt gedeeltelijk  (150mA - 300mA beamcurrent)   (wel voldoende vermogen: 500W, manual goed instelbaar))         |  - Je ruikt pertinax, mogelijk condensator bijna defect.         |  - Beamcurrent slechts instelbaar tussen 300mA - 200mA  (150mA net)        \n- Vervangen door zelf gerepareerde generator (nieuwe voedingscondensator). (6-9-1999). CX-600W. SN: 468  part: FP3114R1. I-beam:   80 - 300mA   100mA: 205W |    200mA 311W |    300mA: 437W\nResolution Status: Resolved"
        output: {
            fault_location: {name: "Generator", machine: "IBM3"},
            fault_symptoms: ["Beamcurrent tussen 300 - 200mA", "Schakelt af op out of tollerance", "ruikt pertinax"],
            fault_reason: [{name: "Niet goed Generator Comdel CX-600S"}, {name: "mogelijk condensator bijna defect"}],
            fault_measures: [{description: "Vervangen door zelf gerepareerde generator (nieuwe voedingscondensator)"}],
            resolution_status: "Resolved"
        }

    Examples 2:
    log_text: "Case-ID: IBM3_C21_19-Jul-16_01-Aug-16\nSources: storing, reparatie\nIssues:\n- Werkte niet, interface kaart gewisseld. | Heeft 1x gewerkt, na 5 sec 200mA beam viel alles uit. | Interface kaart goed.    Storing: B fail. |   Oorzaak:   waarschijnlijk sluiting bij een van de powertransistors.  | \n- Van het beamboard de powertransistors losgehaald. Bij een transistor, was een zwart vlekje in de siliconen isolatie padje te zien (onder transistor).            | Lijkt grafitisatie van de siliconen. Deze vervangen door keramische isolatieplaatjes (beide transistors).            | 7815 voor de zekerheid ook vervangen.  Beamboard AE 02535E4499   powertransistor-unit 67539  99           \nResolution Status: Unknown"
        output: {
            fault_location: {name: "beamboard", machine: "IBM3"},
            fault_symptoms: ["Werkte niet"],
            fault_reason: [{name: "waarschijnlijk sluiting bij een van de powertransistors"}, 
              {name: "een zwart vlekje in de siliconen isolatie padje"}, 
              {name: "Lijkt grafitisatie van de siliconen"}, 
              {name: "Deze vervangen door keramische isolatieplaatjes (beide transistors)"}
              ],
            fault_measures: [{description: "vervangen door keramische isolatieplaatjes (beide transistors)"}],
            resolution_status: "Unknown"
        }

    Example 3:
    log_text: "Case-ID: IBM4_C29_06-Dec-16_06-Dec-16\nSources: Reparatie\nIssues:\n- Cryopomp is gereviseerd door High Vac. Uptime. CTI OB250F cryopomp, SN J06537588 | Na montage bleek dat de voorpomp niet automatisch start met regenereren. PO. 2307 | Deze in servicemode aangezet. Na paar uur was temp 11 K | Echter nieuwe controller communiceert niet met machine   SN: 87F950627 | Oorzaak: Relais--instellingen  (zie hiernaast)       | Aangepast, werkt nu. | PN: 8113036G001. |  | Hallo Paul,09-Dec-16 | Dit heeft te maken met de relais settings. | In de bijlage een overview alsmede de wijze waarop deze aan te passen zijn. We kunnen dit ook samen per telefoon doen indien gewenst. | Settings voor de IBM machine moeten zijn: | Relais 1 = 2nd stage temp 20-22K. | Relais 2 = Regen track | Deze beide signalen gaan naar de IBM controller als input. | Graag de juiste module weer bij de juiste pomp steken in verband met de diode calibratie gegevens van de temperatuur uitlezing. | Met vriendelijke groet \/  Best regards, | William Claassen |  | \nResolution Status: Resolved"
        output: {
            fault_location: {name: "Cryopomp", machine: "IBM4"},
            fault_symptoms: ["voorpomp niet automatisch start met regenereren"],
            fault_reason: [{name: "Relais--instellingen"}],
            fault_measures: [{description: "Relais 1 = 2nd stage temp 20-22K. | Relais 2 = Regen track"}],
            resolution_status: "Resolved"
        }

    Example 4:
    log_text: "Case-ID: IBM4_C41_04-Jul-18_04-Jul-18\nSources: Storing & Reparatie\nIssues:\n- Neutralizer: | IBM proces starte niet. | Reden: Kwam niet door de opstart-procedure heen. (haalde 300 mA niet). | Aanpassing:Waarde verandert in de setup: van 300 naar 200 mA. | Probleem opgelost.\nResolution Status: Resolved"
        output: {
            fault_location: {name: "Neutralizer", machine: "IBM4"},
            fault_symptoms: ["proces starte niet"],
            fault_reason: [{name: "Kwam niet door de opstart-procedure heen. (haalde 300 mA niet)"}],
            fault_measures: [{description: "Waarde verandert in de setup: van 300 naar 200 mA"}],
            resolution_status: "Resolved"
        }

    Example 5:
    log_text: "Case-ID: IBM4_C51_03-Jul-20_03-Jul-20\nSources: Storing & Reparatie\nIssues:\n- Neutralizer: Blijft problemen geven. meerdere keren schoongemaakt, ontlading start gelijk op 300mA \/ spanning is zeer laag: 254V. | Probleem:  geen emissie, daarom start ibm-opstart programma niet door | actie:Nieuwe Ta-cathode, nieuwe boutjes, nieuw diafragma erin. | resultaat: Start goed op, 20 min laten draaien\nResolution Status: Resolved"
        output: {
            fault_location: {name: "Neutralizer", machine: "IBM4"},
            fault_symptoms: ["ontlading start gelijk op 300mA \/ spanning is zeer laag: 254V", "geen emissie", "opstart programma niet door"],
            fault_reason: [],
            fault_measures: [{description: "Nieuwe Ta-cathode, nieuwe boutjes, nieuw diafragma erin"}],
            resolution_status: "Resolved"
        }
  
Now extract entities from the following log: 
Maintenance Log:
    ---
    {{ log_text }}
    ---

    {{ ctx.output_format }}
  "#
}

function ExtractFaultsFromImage(img: image) -> FaultReport[] {
  client CustomGPT4o

  prompt #"
    You are an expert in industrial machine maintenance and repair.

    The following image is a troubleshooting table. Your task is to extract all distinct fault cases.

    **Important rules**:
    - The overall component/system being diagnosed (e.g., from the table title like “Compressor Troubleshooting Procedures”) should be used as the **fault_location**, unless a more specific subcomponent is clearly the root of the issue.
    - If no machine (IBM3 or IBM4) is mentioned in the image, omit it from the output.
    - Do NOT use the component mentioned in the symptom (e.g., a breaker or connector) as the fault location unless it is clearly the root cause.
    - For each `fault_reason`, also extract the **corresponding** corrective action(s) from the same row in the `Corrective Action` or other relevant column as `fault_measures`.
    - Only assign measures that are **explicitly linked** to the given reason (typically matched by the same number from the same row, e.g., Reason 2 → Measure 2 or usually from the same row). Do not merge unrelated measures across multiple causes.
    - Do not output any visual separators, numbering (e.g., "1.", "2.", "🔧 Fault 1", "Fault 2", etc.). Only extract the clean textual content of each field (symptoms, reasons, measures).

    For each fault, extract:
    - `fault_location`: the major component (usually from the table title)
    - `fault_symptoms`: what problem is observed
    - `fault_reason`: possible causes listed
    - `fault_measures`: corrective actions listed
    - `resolution_status`: if stated; otherwise, omit

    Return a valid JSON array of FaultReport objects.
    
    {{ ctx.output_format }}

    {{ _.role("user") }}
    {{ img }}
  "#
}
