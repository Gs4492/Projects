import { useCallback, useEffect, useMemo, useState } from "react";
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

function useOptionalSpeechEvent(eventName, handler) {
  if (useSpeechRecognitionEventHook) {
    useSpeechRecognitionEventHook(eventName, handler);
  }
}

export function useSpeechToText() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [speechError, setSpeechError] = useState("");
  const [isAvailable, setIsAvailable] = useState(false);
  const [needsDevBuild, setNeedsDevBuild] = useState(false);

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
    setSpeechError("");
    setTranscript("");
    setIsListening(true);
  });

  useOptionalSpeechEvent("end", () => {
    setIsListening(false);
  });

  useOptionalSpeechEvent("result", (event) => {
    const nextTranscript = event?.results?.[0]?.transcript || "";
    if (nextTranscript) {
      setTranscript(nextTranscript);
    }
  });

  useOptionalSpeechEvent("error", (event) => {
    setIsListening(false);
    setSpeechError(event?.message || "Speech recognition failed.");
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
    const permission = await speechModule.requestPermissionsAsync();
    if (!permission.granted) {
      setSpeechError("Microphone or speech permission was not granted.");
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
        EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS: 1500,
        EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS: 1500,
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
      needsDevBuild,
      startListening,
      stopListening,
      clearTranscript: () => setTranscript(""),
    }),
    [isAvailable, isListening, transcript, speechError, needsDevBuild, startListening, stopListening]
  );
}