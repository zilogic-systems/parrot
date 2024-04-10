** Settings **
Library  parrot.DTMF

** Test Cases **
Test Verify DTMF Tone Success
    Verify DTMF Tone    0123456789ABCD*#    test/dtmf-tones/all-characters.wav

Test Verify DTMF Tone Fail
    Run Keyword And Expect Error    *    Verify DTMF Tone    0123456789ABCD    test/dtmf-tones/all-characters.wav

Test DTMF Generator
    DTMF Generator    123    test/test.wav
    Verify DTMF Tone    123    test/test.wav