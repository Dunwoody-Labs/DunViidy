<?php
// filepath: c:\Users\elkomaa\Downloads\DunViidy\video-uploader\upload.php

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Check if the video file and email are provided
    if (isset($_FILES['video']) && isset($_POST['email'])) {
        $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
        $video = $_FILES['video'];

        // Validate email
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            echo "Invalid email address.";
            exit;
        }

        // Validate video file
        $allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv'];
        if (!in_array($video['type'], $allowedTypes)) {
            echo "Invalid video format. Only MP4, AVI, MOV, and MKV are allowed.";
            exit;
        }

        if ($video['size'] > 1000000000) { // 1GB limit
            echo "File is too large. Maximum size is 1GB.";
            exit;
        }

        // Save the video file to the server
        $uploadDir = __DIR__ . '/uploads/';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0777, true);
        }

        $filePath = $uploadDir . basename($video['name']);
        if (move_uploaded_file($video['tmp_name'], $filePath)) {
            echo "Video uploaded successfully!";

            // Save email to a text file
            $emailFile = $uploadDir . pathinfo($video['name'], PATHINFO_FILENAME) . '.txt';
            file_put_contents($emailFile, $email);

            echo " Email saved successfully.";
        } else {
            echo "Failed to upload the video.";
        }
    } else {
        echo "Please provide both a video file and an email.";
    }
} else {
    echo "Invalid request method.";
}
?>