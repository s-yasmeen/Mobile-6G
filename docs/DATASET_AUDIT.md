# Dataset Audit

## mmHSense — primary
- Scope: six labeled mmWave ISAC datasets spanning gesture recognition, pose estimation, localization and gait/person identification.
- Signals include Wi-Fi and 5G/mmWave settings across the collection.
- Public companion code documents PyTorch .pth-style dataset structures and a CC BY 4.0 code/repository license.
- Dataset files are distributed separately (documented by the authors via IEEE DataPort); raw files are not redistributed here.
- Research constraint: separate mmHSense task datasets must not be treated as if they were automatically sample-aligned. Phase 2 will inspect downloaded metadata before defining a joint utility/private-label experiment.

## OPERAnet — independent validation
- Approximately 8 hours, two rooms, six participants and six daily activities.
- RF modalities include Wi-Fi CSI, UWB and passive Wi-Fi radar, synchronized with Kinect data.
- The Scientific Data article states public availability through Figshare and describes example loading/analysis code.
- Wi-Fi CSI records include activity/experiment context; UWB description explicitly includes person_id and room/experiment metadata.
- License reported with the open article/dataset documentation: CC BY 4.0.

## Provenance rule
Every experiment must record dataset name/version/source, modality, preprocessing parameters, split seed, model and commit SHA where available. No third-party raw dataset is committed to Git.

## Decision gate
If mmHSense does not expose aligned utility and identity labels for the same observations, it remains the ISAC benchmark but will not be forced into an invalid dual-label experiment. OPERAnet can serve as the principal dual-label privacy/utility study because participant and activity metadata are available together. This decision must be made from the downloaded data schema, not assumption.


## OPERAnet schema verification (official Data Descriptor)
The Wi-Fi CSI directories wificsi1/wificsi2 store one experiment per MAT file. Each row is a received packet and includes timestamp, activity, exp_no, person_id, room_no and 270 complex CSI fields from the 3x3 MIMO x 30-subcarrier configuration. This directly supports activity as the utility label, person_id as the privacy label, and exp_no as the grouping unit. Raw CSI preprocessing must preserve experiment boundaries. The Figshare wificsi1 item reports a CC0 license; license/provenance should therefore be recorded at item/file level rather than assuming one license for every collection component.
