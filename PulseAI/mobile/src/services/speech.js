import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Platform } from "react-native";

let speechModule = null;
let useSpeechRecognitionEventHook = null;

try {
  const speechPackage = require("expo-speech-recognition");
  speechModule = speechPackage.ExpoSpeechRecognitionModule;
  useSpeechRecognitionEventHook = speechPackage.useSpeechRecognitionEvent;
} catch (error) {
  speechModule = null;
  useSpeechRecognitionEventHook = null;
}

const LISTENING_GRACE_MS = 10000;
const COMPLETE_SILENCE_MS = 12000;
const POSSIBLY_COMPLETE_SILENCE_MS = 8000;

function useOptionalSpeechEvent(eventName, handler) {
  if (useSpeechRecognitionEventHook) {
    useSpeechRecognitionEventHook(eventName, handler);
  }
}

export function useSpeechToText() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [speechError, setSpeechError] = useState("");
  const [lastStatus, setLastStatus] = useState("idle");
  const [isAvailable, setIsAvailable] = useState(false);
  const [needsDevBuild, setNeedsDevBuild] = useState(false);
  const listeningStartedAt = useRef(0);
  const transcriptRef = useRef("");

  useEffect(() => {
    let mounted = true;

    if (!speechModule) {
      if (mounted) {
        setIsAvailable(false);
        setNeedsDevBuild(true);
      }
      return () => {
        mounted = false;
      };
    }

    speechModule
      .getStateAsync()
      .then(() => {
        if (mounted) {
          setIsAvailable(true);
          setNeedsDevBuild(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setIsAvailable(false);
          setNeedsDevBuild(true);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  useOptionalSpeechEvent("start", () => {
    listeningStartedAt.current = Date.now();
    setSpeechError("");
    setIsListening(true);
    setLastStatus("listening");
  });

  useOptionalSpeechEvent("end", () => {
    setIsListening(false);
    setLastStatus((current) => (transcriptRef.current ? "captured" : current === "error" ? "error" : "idle"));
  });

  useOptionalSpeechEvent("result", (event) => {
    const nextTranscript = event?.results?.[0]?.transcript || "";
    if (nextTranscript) {
      transcriptRef.current = nextTranscript;
      setTranscript(nextTranscript);
      setSpeechError("");
      setLastStatus("captured");
    }
  });

  useOptionalSpeechEvent("error", (event) => {
    setIsListening(false);

    const rawMessage = event?.message || "Speech recognition failed.";
    const normalized = rawMessage.toLowerCase();
    const listenedFor = Date.now() - listeningStartedAt.current;

    if (normalized.includes("no speech") || normalized.includes("no match")) {
      if (listenedFor < LISTENING_GRACE_MS) {
        setSpeechError("I did not catch that clearly. Please tap again and speak after the beep.");
      } else {
        setSpeechError("No speech was heard. Please tap again and speak clearly.");
      }
      setLastStatus("error");
      return;
    }

    setSpeechError(rawMessage);
    setLastStatus("error");
  });

  const startListening = useCallback(async () => {
    if (!speechModule) {
      setNeedsDevBuild(true);
      setSpeechError(
        Platform.OS === "ios"
          ? "Speech input needs a development build or production app, not Expo Go."
          : "Speech input needs a development build or production app, not Expo Go."
      );
      return false;
    }

    setSpeechError("");
    transcriptRef.current = "";
    setLastStatus("idle");
    const permission = await speechModule.requestPermissionsAsync();
    if (!permission.granted) {
      setSpeechError("Microphone or speech permission was not granted.");
      setLastStatus("error");
      return false;
    }

    speechModule.start({
      lang: "en-US",
      interimResults: true,
      maxAlternatives: 1,
      continuous: false,
      addsPunctuation: true,
      requiresOnDeviceRecognition: false,
      androidIntentOptions: {
        EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS: COMPLETE_SILENCE_MS,
        EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS: POSSIBLY_COMPLETE_SILENCE_MS,
      },
      contextualStrings: [
        "blood pressure",
        "BP",
        "sugar",
        "whiskey",
        "vodka",
        "beer",
        "small peg",
        "large peg",
        "salty snacks",
        "water",
      ],
    });
    return true;
  }, []);

  const stopListening = useCallback(() => {
    if (speechModule) {
      speechModule.stop();
    }
  }, []);

  return useMemo(
    () => ({
      isAvailable,
      isListening,
      transcript,
      speechError,
      lastStatus,
      needsDevBuild,
      startListening,
      stopListening,
      clearTranscript: () => {
        transcriptRef.current = "";
        setTranscript("");
        setSpeechError("");
        setLastStatus("idle");
      },
    }),
    [isAvailable, isListening, transcript, speechError, lastStatus, needsDevBuild, startListening, stopListening]
  );
}
