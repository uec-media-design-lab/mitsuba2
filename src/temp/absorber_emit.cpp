#include <mitsuba/core/properties.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/core/spectrum.h>
#include <mitsuba/render/emitter.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/render/shape.h>
#include <mitsuba/render/texture.h>

NAMESPACE_BEGIN(mitsuba)

template <typename Float, typename Spectrum>
class Absorber final : public Emitter<Float, Spectrum> {
public:
    MTS_IMPORT_BASE(Emitter, m_flags, m_shape, m_medium)
    MTS_IMPORT_TYPES(Scene, Shape, Texture)

    Absorber(const Properties &props) : Base(props) {
        Throw("Found a 'to_world' transformation -- this is not allowed. "
                  "The absorber inherits this transformation from its parent "
                  "shape.");
    }

    /** MEMO: by Shunji Kiuchi
     *  Should this class absorb the pixel information propagated by the ray in this fuction??
     */
    Spectrum eval(const SurfaceInteraction3f &si, Mask active) const override {
        MTS_MASKED_FUNCTION(ProfilerPhase::EndpointEvaluate, avtive);

        return 0.f;
    }

    MTS_DECLARE_CLASS()
private:
    Bitmap::FileFormat m_file_format;
    Bitmap::PixelFormat m_pixel_format;
    Struct::Type m_component_format;
    fs::path m_dest_file;
    std::vector<std::string> m_channels;
};


MTS_IMPLEMENT_CLASS_VARIANT(Absorber, Emitter)
MTS_EXPORT_PLUGIN(Absorber, "Absorber")
NAMESPACE_END(mitsuba)
