### Development notes

- Important medical concepts are defined as Python objects under ssmixtwins.objects:

  - Patient
  - Hospital
  - Admission
  - Prescription and injection order
  - Laboratory tests and specimens
    Attributes of these objects are validated inside \_\_init\_\_().

- These objects are used in ssmixtwins.segments and ssmixtwins.messages, etc.

- You should move argument validation logics at message levels, not segment level.
  Specifications of segments can slightly vary among messages. Therefore, segment-level argument validations should be avoided.
  Some constant segment fields can be safely validated at segment levels (e.g., MSH, PID, PV1).

- All ways make sure to allow empty strings ("") for optional fields upon validation.

- Occasionally, you may need to use '""' (double quotes) as a string value.
  This is not an empty string, but a visible "". It is used for HL7 fields that are requried, but the value is hard to determine. This practice is officially documented for some parts of SS-MIX2.
  For example, in RXE-3 (minimum_dose), if the minimum dose is hard to determine (e.g., ointment), it should be '""', not an empty string because RXE-3 is a required field.
  Be careful, you sometimes encounter '""' in the code.
  Consider this as the official fallback. Do not use this on your own discretion.
