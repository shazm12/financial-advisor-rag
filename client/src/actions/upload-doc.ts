"use server";

export async function uploadDocToAPI(file: File) {

    try {
        if (!file) {
            return {
                success: false,
                error: "No file provided"
            };
        }

        if (file.size === 0) {
            return {
                success: false,
                error: "File is empty"
            };
        }

        const MAX_FILE_SIZE = 10 * 1024 * 1024;

        if (file.size > MAX_FILE_SIZE) {
            return {
                success: false,
                error: "File size greater than 10 MB"
            };
        }
        const allowedTypes = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
        if (!allowedTypes.includes(file.type)) {
            return { success: false, error: "Invalid file type" };
        }

        const apiFormData = new FormData();
        apiFormData.append("file", file);

        const response = await fetch(`${process.env.API_URL}/api/extraction/process`, {

            method: "POST",
            body: apiFormData
        });

        if (!response.ok) {
            const error = await response.json();
            return {
                success: false,
                error: error.detail || "Upload Failed"
            }
        }

        const result = await response.json();

        return {
            success: true,
            status: result.status,
            description: result.description,
            sessionId: result.session_id
        };

    }
    catch (error) {
        console.error("Upload error:", error);
        return {
            success: false,
            error: "Failed to upload file to server"
        };
    }
}