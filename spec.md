# LipReader

## Product & Technical Specification (v1.0)

---

# 1. Executive Summary

## Project Name

**LipReader**

## Goal

Develop a production-ready web application capable of converting lip movements into text using a pretrained Visual Speech Recognition (VSR) model.

The first version focuses on a single speaker and visual-only transcription while maintaining an architecture that can evolve into a full Audio-Visual Speech Recognition (AVSR) platform.

---

# 2. Vision

Build a modular, maintainable, production-quality lip-reading platform rather than a research prototype.

The system must:

* support uploaded videos
* support real-time webcam inference
* require no model training
* use pretrained VSR models
* allow future model replacement
* separate frontend and backend completely
* remain platform-independent

---

# 3. MVP Scope

## Included

* MP4 upload
* WebM upload
* Live webcam
* Single speaker
* Visual-only speech recognition
* Raw transcript
* Confidence score
* Progress tracking
* REST APIs
* WebSocket streaming
* Automatic device detection
* Local development on macOS
* Future Linux deployment

---

## Future Versions

* Multiple speakers
* Audio + video fusion
* Speaker diarization
* Subtitle generation
* Translation
* Grammar correction
* Streaming subtitles
* Cloud deployment
* Authentication
* Batch processing

---

# 4. Success Criteria

Functional

* Upload a video
* Receive transcript
* Display confidence
* Stream webcam predictions
* Complete processing for videos under two minutes

Non-functional

* Modular
* Extensible
* Testable
* Replaceable model layer
* Production-grade codebase

---

# 5. Technology Stack

## Frontend

* Next.js (App Router)
* TypeScript
* React
* Tailwind CSS
* Native WebSocket
* Fetch API

---

## Backend

* Python 3.12+
* FastAPI
* LangGraph
* Pydantic
* OpenCV
* FFmpeg
* MediaPipe
* PyTorch

---

## ML

Initial Model

* AV-HuBERT

Future

* VSR-T
* RAVen
* E2EAVSR
* Audio-Visual models

---

# 6. Repository Structure

```
lip-reader/

├── frontend/
│
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── lib/
│   ├── styles/
│   ├── types/
│   └── public/
│
└── backend/
    │
    ├── app/
    │
    ├── presentation/
    │
    ├── application/
    │
    ├── domain/
    │
    ├── infrastructure/
    │
    ├── graph/
    │
    ├── services/
    │
    ├── models/
    │
    ├── preprocessing/
    │
    ├── tracking/
    │
    ├── inference/
    │
    ├── decoding/
    │
    ├── schemas/
    │
    ├── config/
    │
    ├── utils/
    │
    ├── tests/
    │
    └── main.py
```

---

# 7. Architecture

```
                    Next.js

      Upload / Webcam / Progress UI
                 │
                 ▼
──────────────────────────────────────

            FastAPI

         REST + WebSocket

                 │

          LangGraph Workflow

                 │

         Application Services

                 │

        ML / CV Infrastructure

                 │

      AV-HuBERT + OpenCV + FFmpeg
```

---

# 8. Clean Architecture

```
Presentation
    │
Application
    │
Domain
    │
Infrastructure
```

## Presentation

* REST Controllers
* WebSocket Controllers

---

## Application

* LangGraph
* Use Cases
* Pipeline Orchestration

---

## Domain

* Pipeline Context
* Business Rules
* Interfaces
* Contracts

---

## Infrastructure

* FFmpeg
* OpenCV
* MediaPipe
* AV-HuBERT
* File Storage

---

# 9. LangGraph Design

LangGraph orchestrates the pipeline.

It does NOT perform image processing.

Workflow:

```
START

↓

Validate Input

↓

Preprocess Video

↓

Run Inference

↓

Decode Output

↓

Build Response

↓

END
```

Each node delegates work to services.

---

# 10. Pipeline Flow

## Uploaded Video

```
Client

↓

POST /api/v1/lipread

↓

Validation

↓

Temporary Storage

↓

Frame Extraction

↓

FPS Normalization

↓

Face Detection

↓

Face Tracking

↓

Mouth Extraction

↓

Tensor Creation

↓

AV-HuBERT

↓

Decoder

↓

Transcript

↓

JSON Response
```

---

## Live Webcam

```
Browser

↓

JPEG/WebP Frames

↓

WebSocket

↓

Frame Buffer

↓

Face Detection

↓

Tracking

↓

Mouth Crop

↓

Inference

↓

Partial Prediction

↓

Frontend
```

---

# 11. Pipeline Context

Every service receives and returns the same immutable PipelineContext.

```
PipelineContext

video

metadata

frames

tracks

mouth_frames

tensor

logits

transcript

confidence

metrics

errors
```

This object is the only data passed between LangGraph nodes.

---

# 12. Core Services

## ValidationService

Responsibilities

* file validation
* duration validation
* codec validation

---

## VideoService

Responsibilities

* decode video
* extract metadata
* normalize FPS

---

## FaceDetectionService

Uses MediaPipe initially.

Future detectors should be interchangeable.

---

## TrackingService

Responsibilities

* initialize tracking
* update tracking
* re-detect when lost

---

## MouthExtractionService

Produces normalized mouth crops.

---

## TensorService

Creates tensors expected by the model.

---

## InferenceService

Responsibilities

* load model
* run inference
* return logits

---

## DecoderService

Responsibilities

* decode logits
* generate transcript
* calculate confidence

---

## MetricsService

Collects

* processing time
* inference time
* preprocessing time
* device
* FPS

---

# 13. Model Abstraction

Never depend directly on AV-HuBERT.

```
BaseVSRModel

predict()

↓

AVHuBERTModel

↓

FutureModel

↓

ModelFactory
```

This enables future model replacement without changing the API or workflow.

---

# 14. Model Lifecycle

Application Startup

↓

Detect Device

↓

Load Model

↓

Keep Model Resident

↓

Serve Requests

↓

Shutdown Gracefully

The model is loaded exactly once.

---

# 15. Device Selection

Priority

1. CUDA
2. Apple MPS
3. CPU

The selected device is included in processing metrics.

---

# 16. Video Requirements

Formats

* mp4
* webm

Maximum Duration

* 2 minutes

Normalization

* fixed FPS
* fixed resolution
* RGB conversion

---

# 17. API Specification

## REST

### POST

```
/api/v1/lipread
```

Returns

```
{
    transcript,

    confidence,

    metrics
}
```

---

### GET

```
/health
```

---

## WebSocket

```
/ws/live
```

Client sends

* compressed image frames

Server returns

* partial transcript
* final transcript
* confidence
* progress

---

# 18. Response Format

```
{
  "transcript": "...",

  "confidence": 0.93,

  "metrics": {
      "device":"mps",
      "processingTime":3.7,
      "inferenceTime":1.9
  }
}
```

---

# 19. Progress States

```
Uploading

↓

Validating

↓

Extracting Frames

↓

Detecting Face

↓

Tracking Face

↓

Extracting Mouth

↓

Running Model

↓

Decoding

↓

Completed
```

Frontend displays current stage.

---

# 20. Error Handling

Validation Errors

* unsupported format
* duration exceeded
* corrupted file

Processing Errors

* face not detected
* tracking failure
* model failure

System Errors

* device unavailable
* model unavailable
* internal server error

---

# 21. Temporary Storage

```
uploads/

job-id/

input.mp4

frames/

mouth/

```

Automatically removed after processing.

---

# 22. Logging

Simple structured logging.

Every request includes

* request id
* processing time
* model
* device
* success/failure

---

# 23. Testing

## Unit

* services
* utilities
* model adapters

---

## Integration

* API
* preprocessing
* inference

---

## End-to-End

* upload flow
* webcam flow
* transcript generation

---

# 24. Security

Current MVP

* no authentication
* local development

Basic protections

* upload validation
* size limits
* MIME validation

Future

* authentication
* authorization
* rate limiting

---

# 25. Performance Targets

Upload Processing

* videos ≤ 2 minutes

Live Mode

* best-effort latency on local hardware

Memory

* model loaded once

Concurrency

* one active user (MVP)

---

# 26. Coding Standards

* Python type hints
* Pydantic validation
* Black formatting
* Ruff linting
* Clean Architecture
* Dependency Injection where appropriate
* No business logic in controllers
* No ML code inside LangGraph nodes

---

# 27. Implementation Phases

## Phase 1

Project setup

* repositories
* architecture
* FastAPI
* Next.js
* CI
* testing

Deliverable

Application skeleton.

---

## Phase 2

Video pipeline

* uploads
* validation
* FFmpeg
* frame extraction

Deliverable

Backend preprocessing.

---

## Phase 3

Computer vision

* MediaPipe
* tracking
* mouth extraction

Deliverable

Stable mouth crop pipeline.

---

## Phase 4

Model integration

* AV-HuBERT
* model abstraction
* inference service

Deliverable

End-to-end transcription.

---

## Phase 5

Frontend

* upload
* webcam
* progress
* transcript
* confidence

Deliverable

Complete user interface.

---

## Phase 6

Live mode

* WebSocket
* frame streaming
* partial predictions

Deliverable

Real-time lip reading.

---

## Phase 7

Testing & optimization

* unit
* integration
* E2E
* performance tuning

Deliverable

Production-ready MVP.

---

# 28. Future Roadmap

* Multiple speakers
* Audio-visual speech recognition
* Speaker diarization
* Subtitle export (SRT/VTT)
* Grammar correction
* Translation
* Batch processing
* Docker deployment
* Kubernetes
* Authentication
* Cloud storage
* Model marketplace
* Additional VSR backends
* Benchmark dashboard

---

# 29. Engineering Principles

1. Keep orchestration separate from computer vision.
2. Hide all model implementations behind interfaces.
3. Treat LangGraph as the workflow engine, not the inference engine.
4. Make every service independently testable.
5. Normalize all inputs before inference.
6. Load the model exactly once.
7. Keep the frontend model-agnostic.
8. Design every component so future VSR models can replace AV-HuBERT without changing external APIs.
9. Favor composition over tight coupling.
10. Build the MVP with simplicity first, while preserving clear extension points for future capabilities.

