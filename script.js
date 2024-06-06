document.addEventListener('DOMContentLoaded', () => {
    fetch('0023.json')
        .then(response => response.json())
        .then(data => {
            initializeVehicleDropdown(data);
        });

    const vehicleSelect = document.getElementById('vehicleSelect');
    const partSelect = document.getElementById('partSelect');
    const qrCodeDiv = document.getElementById('qrcode');

    vehicleSelect.addEventListener('change', () => {
        const selectedVehicle = vehicleSelect.value;
        updatePartDropdown(selectedVehicle);
    });

    partSelect.addEventListener('change', () => {
        const selectedVehicle = vehicleSelect.value;
        const selectedPart = partSelect.value;
        generateQRCode(selectedVehicle, selectedPart);
    });

    function initializeVehicleDropdown(data) {
        data.forEach(vehicle => {
            const option = document.createElement('option');
            option.value = vehicle.vehicle_id;
            option.textContent = vehicle.vehicle_id;
            vehicleSelect.appendChild(option);
        });
    }

    function updatePartDropdown(vehicleId) {
        partSelect.innerHTML = '<option value="">Метка</option>';
        partSelect.disabled = true;
        qrCodeDiv.innerHTML = '';

        fetch('0023.json')
            .then(response => response.json())
            .then(data => {
                const vehicle = data.find(v => v.vehicle_id === vehicleId);
                if (vehicle) {
                    vehicle.details.forEach(detail => {
                        const option = document.createElement('option');
                        option.value = detail.part;
                        option.textContent = detail.part;
                        partSelect.appendChild(option);
                    });
                    partSelect.disabled = false;
                }
            });
    }

    function generateQRCode(vehicleId, partName) {
        fetch('0023.json')
            .then(response => response.json())
            .then(data => {
                const vehicle = data.find(v => v.vehicle_id === vehicleId);
                if (vehicle) {
                    const part = vehicle.details.find(d => d.part === partName);
                    if (part) {
                        qrCodeDiv.innerHTML = ''; // Очищаем содержимое DIV перед созданием нового QR-кода
                        const qr = new QRCode(qrCodeDiv, {
                            text: part.code,
                            width: 128,
                            height: 128
                        });
                        qr.makeImage(); // Генерируем изображение QR-кода
                    }
                }
            });
    }
    
});
