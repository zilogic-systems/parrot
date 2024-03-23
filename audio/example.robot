** Settings **

Library  parrot.Audio

** Test Cases **

Record and Playback Test
       Audio Set Input Device  9
       Audio Set Output Device  9
       Audio Start Recording
       Sleep  5
       Audio Stop Recording    test.wav
       Audio Play File  test.wav
