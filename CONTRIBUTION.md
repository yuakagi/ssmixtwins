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
